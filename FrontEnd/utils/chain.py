from operator import itemgetter
import streamlit as st
from dotenv import load_dotenv
from qdrant_client.http import models as rest
from utils.qdrant_client_instance import QdrantClientInit

load_dotenv()

global_qdrant_client = QdrantClientInit.get_qdrant_client()

class RagChain:

    def __init__(self):
        self.retriever = None
        self.qdrant_client = global_qdrant_client
        self.qdrant_instance = None
        self.llm = llm

    def __conn_db(self):
        if self.qdrant_instance is None:
            self.qdrant_instance = Qdrant(
                self.qdrant_client,
                embeddings = OpenAIEmbeddings(),
                collection_name="all_ons_docs_recursive",
            )
            
        return self.qdrant_instance

    def set_retriever_as_custom(self, document_path):

        retriever = self.__conn_db().as_retriever(
            search_kwargs=dict(
                k=10,
                filter = rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="metadata.source",
                            match=rest.MatchValue(value='../data/ons_documents/' + document_path)
                        )
                    ]
                )
            )
        )

        self.retriever =  MultiQueryRetriever.from_llm(
            retriever=retriever, llm=self.llm
        )
    def set_retriever_as_hybrid(self):
        retriever = self.__conn_db().as_retriever(search_kwargs=dict(
                k=1000000))
        docs = retriever.get_relevant_documents("o")
        bm25_retriever = BM25Retriever.from_documents(
                    docs)
        dense_retriever = self.__conn_db().as_retriever(search_kwargs=dict(
                k=10))
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, dense_retriever], weights=[0.6, 0.4])
        self.retriever = ensemble_retriever

        
        

    def set_retriever_as_alldocs(self):
        self.retriever = self.__conn_db().as_retriever(
            search_kwargs={'k': 10}
        )

    def set_retriver_as_uploaded(self):
        with open("uploaded_file.pdf", mode='wb') as w:
            w.write(st.session_state.uploaded_file.getvalue())
        loader = PyPDFLoader('uploaded_file.pdf')
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        uploaded_doc_db = FAISS.from_documents(docs, embeddings)

        self.retriever = uploaded_doc_db.as_retriever()

    
    def get_rag_chain(self):
        CONTEXTUALIZE_Q_SYSTEM_PROMPT = """Dada um histórico de conversa e a última pergunta do usuário \
        que pode fazer referência ao contexto no histórico da conversa, formule uma pergunta independente \
        que possa ser entendida sem o histórico da conversa. NÃO responda à pergunta, \
        apenas reformule-a se necessário e, caso contrário, retorne-a sem alterações.  """

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        contextualize_q_chain = contextualize_q_prompt | self.llm | StrOutputParser()
        

        def contextualized_question(input: dict):
            if input.get("chat_history"):
                return contextualize_q_chain
            else:
                return input["question"]

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        prompt = """Respire profundamente e seja conciso. Apenas utilize utilize a parte do contexto que esteja relacionada as entidades chaves da pergunta.
        Responda passo à pergunta baseado apenas no contexto a seguir

        {formatted_context}

        Pergunta: {question}

E retorne o trecho do contexto utilizado para responder a pergunta e o documento a qual se refere.
        """

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", prompt),
            ]
        )

        print(qa_prompt)
            
        chain = (
            RunnablePassthrough.assign(formatted_context=(lambda x: format_docs(x['context'])))
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )

        rag = RunnablePassthrough.assign(
            contextualized_question=contextualized_question
        ).assign(
            context=itemgetter('contextualized_question') | self.retriever
        ).assign(
            answer=chain
        )
        return rag