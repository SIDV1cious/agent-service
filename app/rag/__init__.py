from dotenv import load_dotenv
load_dotenv()
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_milvus import Milvus, BM25BuiltInFunction
from app.core.config import settings
from app.core.logging import get_logger
from app.rag.pipeline import RAGPipeline
from app.rag.retriever import RagRetriever

logger = get_logger(__name__)

# 1.初始化向量模型
embeddings = DashScopeEmbeddings(
        model="qwen3.7-text-embedding-flash"
    )

# 2.初始化VectorStore
vector_store = Milvus(
    embedding_function=embeddings,
    collection_name="insurance_collection",
    connection_args={"uri":settings.rag.milvus_url},
    auto_id=True,
    vector_field=["dense","sparse"],
    builtin_function=BM25BuiltInFunction(
        input_field_names="text",
        output_field_names="sparse",
        analyzer_params={"type":"chinese"},
        function_name="insurance_sparse_function"
    )
)

# 3.初始化Pipeline和Retriever
pipeline = RAGPipeline(vector_store)
retriever = RagRetriever(vector_store)

logger.info("RAG中的pipeline和retriever初始化完成")

# 4.提供一个关闭的方法
def close_rag():
    pipeline.close()
    vector_store.client.close()
    logger.info("RAG资源关闭完成~")



__all__ = ["pipeline", "retriever", "close_rag"]