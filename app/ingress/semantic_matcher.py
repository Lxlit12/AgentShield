from sentence_transformers import SentenceTransformer
import numpy as np


class SemanticScopeMatcher:

    def __init__(self, threshold=0.35):

        self.threshold = threshold

        print("Loading MiniLM model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # Security/domain scope descriptions
        self.allowed_scopes = [

    # Programming
    "Python programming, algorithms, data structures, sorting, searching, and coding questions",

    "software development, programming languages, debugging, APIs, databases, and application development",

    # AI / ML
    "artificial intelligence, machine learning, deep learning, neural networks, CNNs, transformers, and NLP",

    # Cybersecurity
    "cybersecurity, application security, authentication, authorization, vulnerabilities, and secure software",

    # AgentShield
    "AgentShield architecture, security policies, AI agent security, prompt injection, and policy enforcement",

    # MCP
    "Model Context Protocol, MCP servers, MCP tools, tool calls, authorization, and tool security",
        ]

        self.scope_embeddings = self.model.encode(
            self.allowed_scopes,
            normalize_embeddings=True
        )

        print("MiniLM model loaded.")


    def check_scope(self, prompt: str):

        prompt_embedding = self.model.encode(
            prompt,
            normalize_embeddings=True
        )

        similarities = np.dot(
            self.scope_embeddings,
            prompt_embedding
        )

        max_similarity = float(
            np.max(similarities)
        )

        best_scope_index = int(
            np.argmax(similarities)
        )

        best_scope = self.allowed_scopes[
            best_scope_index
        ]

        allowed = max_similarity >= self.threshold

        return {
            "allowed": allowed,
            "similarity": max_similarity,
            "threshold": self.threshold,
            "matched_scope": best_scope
        }