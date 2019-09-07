import torch.nn as nn
from model import ProductCategorizer
from torch.utils import data
from Dataset import Dataset
import csv
import torch

cats = 21

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# We create the dataloader.
vocab_mapping = {}
vocab_count = 1
src_data = []
tgt_data = []

print("Loading dataset...")
with open('./products.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    next(spamreader)
    for row in spamreader:
        name = row[1]
        words = name.split(" ")
        sentenceArray = []
        for word in words:
            if word not in vocab_mapping:
                vocab_mapping[word] = vocab_count
                vocab_count += 1
            sentenceArray.append(vocab_mapping[word])
        src_data.append(torch.LongTensor(sentenceArray))
        department = int(row[3]) - 1
        tgt_data.append(torch.LongTensor([department]))

print("Loaded dataset.")

model = ProductCategorizer(vocab_count, cats)
model = model.to(device)

criterium = nn.CrossEntropyLoss().to(device)
optimizer = torch.optim.Adam(model.parameters(),lr=0.01,weight_decay=1e-4)

# Map 

data = Dataset(src_data, tgt_data, 20 * 1000, batch_size_sents=1000)

data.create_order()

for epoch in range(100000):
        # Definition of inputs as variables for the net.
        # requires_grad is set False because we do not need to compute the 
        # derivative of the inputs.
        samples = data.next()
        batch = samples[0]
        #batch.cuda()


        # Set gradient to 0.
        optimizer.zero_grad()
        # Feed forward.
        src = batch.get('source')
        src = src.transpose(0, 1)
        #print("Batch: " + str(src.size()))
        src_mask = batch.get("src_mask")
        src_length = batch.get("src_length")

        targets = batch.get('target_input')

        pred = model(src, src_mask, src_length)
        #print("Pred: " + str(pred.size()))
        # Loss calculation.
 
        loss = criterium(pred,targets)
        # Gradient calculation.
        loss.backward()
    
        # Print loss every 10 iterations.
        max_index = pred.max(dim = 1)[1]
        correct = float((max_index == targets).sum()) / float(max_index.size(0))
        print('Loss {:.4f} at epoch {:d}: {:.4f}'.format(loss.item(),epoch, correct))
        # Model weight modification based on the optimizer. 
        optimizer.step()
        if epoch % 4000 == 0:
            torch.save(model.state_dict(), "./model_e" + str(epoch) + ".pt")


