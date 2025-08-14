#!/usr/bin/env python
import os
import numpy as np
import re
from ampligraph.latent_features.layers.scoring import TransE
from ampligraph.utils import save_model, restore_model

class MemoryManager:
    def __init__(self, **kwargs):
        self.triples = set()
        self.model = None
        self.entity_index = {}
        self.index_entity = {}
        
        # Default model parameters
        self.model_params = kwargs
        # {
        #     'k': 100,               # Embedding dimension
        #     'epochs': 100,           # Training iterations
        #     'eta': 5,                # Number of corruptions
        #     'batches_count': 10,     # Batch size
        #     'embedding_model_params': {'normalize_ent_emb': False}
        # }

    def _extract_triples(self, text):
        """Basic rule-based triple extraction (replace with NLP model in production)"""
        triples = []
        # Pattern 1: "X [relation] Y" 
        matches = re.findall(r'(\w+)\s+(is|has|likes|knows|created|uses|needs)\s+(\w+)', text)
        for match in matches:
            triples.append((match[0].lower(), match[1].lower(), match[2].lower()))
        
        # Pattern 2: "X of Y is Z"
        matches = re.findall(r'(\w+)\s+of\s+(\w+)\s+is\s+(\w+)', text)
        for match in matches:
            triples.append((match[1].lower(), match[0].lower(), match[2].lower()))
            
        return triples

    def extract_memory_from_conversation(self, conversation_history):
        """Extract knowledge triples from conversation history"""
        new_triples = set()
        
        for utterance in conversation_history:
            extracted = self._extract_triples(utterance)
            for triple in extracted:
                # Filter out trivial relations
                if triple[1] not in ['a', 'the', 'and']:
                    new_triples.add(triple)
        
        # Update knowledge graph
        self.triples.update(new_triples)
        
        # Train KG embeddings if we have triples
        if self.triples:
            self._train_model()
            
        return list(new_triples)

    def _train_model(self):
        """Train knowledge graph embeddings"""
        # Convert to numpy array for AmpliGraph
        triples_array = np.array(list(self.triples))
        
        # Create entity mapping
        all_entities = set(np.concatenate([triples_array[:,0], triples_array[:,2]]))
        self.entity_index = {ent: idx for idx, ent in enumerate(all_entities)}
        self.index_entity = {idx: ent for ent, idx in self.entity_index.items()}
        
        # Initialize and train model
        self.model = TransE(**self.model_params)
        self.model.fit(triples_array)

    def save_to_file(self, file_path):
        """Save knowledge graph to file"""
        # Save triples
        with open(file_path + '.tsv', 'w') as f:
            for triple in self.triples:
                f.write(f"{triple[0]}\t{triple[1]}\t{triple[2]}\n")
        
        # Save embeddings model
        if self.model:
            save_model(self.model, file_path + '_model')

    def load_from_file(self, file_path):
        """Load knowledge graph from file"""
        # Load triples
        self.triples = set()
        if os.path.exists(file_path + '.tsv'):
            with open(file_path + '.tsv', 'r') as f:
                for line in f:
                    s, p, o = line.strip().split('\t')
                    self.triples.add((s, p, o))
        else:
            print("Triple file not found.")
            return
        # Load embeddings model if available
        try:
            self.model = restore_model(file_path + '_model')
            # Rebuild entity index
            triples_array = np.array(list(self.triples))
            all_entities = set(np.concatenate([triples_array[:,0], triples_array[:,2]]))
            self.entity_index = {ent: idx for idx, ent in enumerate(all_entities)}
            self.index_entity = {idx: ent for ent, idx in self.entity_index.items()}
        except Exception:
            print("Embedding model not found. Train with extract_memory_from_conversation()")

    def find_by_keyword(self, keyword, topn=5):
        """Find related entities using KG embeddings"""
        keyword = keyword.lower()
        results = set()
        
        # 1. Direct string match
        for triple in self.triples:
            if keyword in triple[0] or keyword in triple[1] or keyword in triple[2]:
                results.add(triple)
        
        # 2. Semantic search using embeddings
        if self.model and keyword in self.entity_index:
            entity_idx = self.entity_index[keyword]
            entity_embedding = self.model.get_embeddings([str(entity_idx)], 
                                                        embedding_type='entity')
            
            # Find most similar entities
            all_embeddings = self.model.get_embeddings(
                list(self.index_entity.keys()), 
                embedding_type='entity'
            )
            
            # Cosine similarity calculation
            norms = np.linalg.norm(all_embeddings, axis=1)
            normalized_emb = all_embeddings / norms[:, None]
            sim = np.dot(normalized_emb, entity_embedding[0] / np.linalg.norm(entity_embedding[0]))
            top_indices = np.argsort(sim)[-topn-1:-1][::-1]
            
            # Get triples for similar entities
            for idx in top_indices:
                entity = self.index_entity[idx]
                for triple in self.triples:
                    if entity in triple[0] or entity in triple[2]:
                        results.add(triple)
        
        return list(results)