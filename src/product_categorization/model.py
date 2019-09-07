import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_packed_sequence, pack_padded_sequence
# Source https://bastings.github.io/annotated_encoder_decoder/

class Encoder(nn.Module):
    """Encodes a sequence of word embeddings"""
    def __init__(self, input_size, hidden_size, num_layers=1, dropout=0.):
        super(Encoder, self).__init__()
        self.num_layers = num_layers
        self.rnn = nn.GRU(input_size, hidden_size, num_layers, 
                          batch_first=True, bidirectional=False, dropout=dropout)
        
    def forward(self, x, mask, lengths):
        """
        Applies a bidirectional GRU to sequence of embeddings x.
        The input mini-batch x needs to be sorted by length.
        x should have dimensions [batch, time, dim].
        """
        #print("X: " + str(x.size()))
        #print("Lengths: " + str(lengths.size()))
        packed = pack_padded_sequence(x, lengths, batch_first=True, enforce_sorted=False)
        output, final = self.rnn(packed)
        output, _ = pad_packed_sequence(output, batch_first=True)

        # we need to manually concatenate the final states for both directions
        return output, final

class ProductCategorizer(nn.Module):

    def __init__(self, vocab_size, outputCategoryCount):
        super(ProductCategorizer, self).__init__()
        embedding_size = 64
        self.embedding = nn.Embedding(vocab_size, embedding_size, padding_idx=0)
        self.encoder = Encoder(embedding_size, 64)
        self.fc = nn.Linear(64, 32)
        self.fc2 = nn.Linear(32, outputCategoryCount)

    def forward(self, src, src_mask, src_lengths):
        #print(src.size())
        embedding = self.embedding(src)
        #print(embedding.size())
        hidden, final = self.encoder(embedding, src_mask, src_lengths)
        result = self.fc2(self.fc(final)).squeeze(0)
        #print("Result: " + str(result.size()))
        categorization = torch.nn.functional.softmax(result, dim=1)
       #print(categorization)
        return categorization

