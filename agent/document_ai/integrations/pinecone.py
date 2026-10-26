def vector_store(index_name, embeddings, namespace):
    """Provide a trusted user namespace and a dimension-compatible embedding model.
    Optional factory only; indexing and retrieval are not called by local mode.
    """
    if not index_name or not namespace: raise ValueError('Index and scoped namespace are required')
    from langchain_pinecone import PineconeVectorStore
    return PineconeVectorStore(index_name=index_name, embedding=embeddings, namespace=namespace)
