import pdb
import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from sklearn.metrics import precision_recall_fscore_support
## write 
trainset = torchvision.datasets.ImageFolder(
    root='knee/train', 
    transform=torchvision.transforms.Compose([
        torchvision.transforms.RandomHorizontalFlip(p=0.5),
        torchvision.transforms.GaussianBlur((3,3)),
        torchvision.transforms.RandomAffine(degrees=15,scale= (0.9,1.1),translate=(0.1,0.1), shear=0.25),
        torchvision.transforms.ToTensor()
    ])  
) #this loads all the images and turns them into numbers so that computer can understand it
testset = torchvision.datasets.ImageFolder(
    root='knee/test', 
    transform=torchvision.transforms.Compose([
        torchvision.transforms.RandomHorizontalFlip(p=0.5),
        torchvision.transforms.GaussianBlur((3,3)),
        torchvision.transforms.RandomAffine(degrees=15,scale= (0.9,1.1),translate=(0.1,0.1), shear=0.25),
        torchvision.transforms.ToTensor()
    ])  
)
writer = SummaryWriter("runs/transformation")

train_dataloader = torch.utils.data.DataLoader(trainset, batch_size=15, shuffle=True)
#this shuffles the set and then gets the images(demonstrated as numbers ) in batches of 8 
test_dataloader = torch.utils.data.DataLoader(testset, batch_size=15, shuffle=True)
cnn_neural_network = torchvision.models.resnet18(pretrained=True)
cnn_neural_network.fc = torch.nn.Linear(in_features=512, out_features=5, bias=True)
#infuture is 
#outfeature is benign or mallignant
cost_function = nn.CrossEntropyLoss()
#creates a cost funtion(least squares )
gradient_descent = optim.Adam(cnn_neural_network.parameters()) 
#RESEARCH ADAM
#starts a gradiant descent with a learning range of 0.001
#F1 FOR BOTH TRAINING AND TESTING SHOULD BE OVER 0.7, TRY NEW WAYS
count=0
#30-45 minutes
for epoch in range(5):  # loop over the dataset multiple times to make it more precia=
    for training_data in train_dataloader: #traverse over the batches
        # get the inputs; data is a list of [inputs(images), labels(benign or mallignant)]
        count+=1
        #count the number of data
       
        #starts testing in every fifth data
        if count % 5 == 0:
            #testing mode
            cnn_neural_network.eval()

            #get the images and labels
            test_data_inputs, test_data_labels = iter(test_dataloader).next()
            #create the model according to test data
            model_predictions_test = cnn_neural_network(test_data_inputs)
            #cost function of the test data
            cost_test = cost_function(model_predictions_test, test_data_labels)
            #back to training mode
            precision, recall, test_f1, support = precision_recall_fscore_support(test_data_labels,
                                                torch.argmax(model_predictions_test, dim=1),
                                                zero_division=0,
                                                labels=(0,1,2,3,4))
            cnn_neural_network.train()
            writer.add_scalar('testing_cost', cost_test, count)
            for index, label in enumerate(test_f1):
                writer.add_scalar('testing_label_'+str(index), label, count)
                
            

        training_data_inputs, training_data_labels = training_data
        
        # zero the parameter gradients
        gradient_descent.zero_grad()
        
        # forward + backward + optimize
        model_predictions = cnn_neural_network(training_data_inputs)
        #recreate the cost function according to the new data loaded
        precision, recall, f1, support = precision_recall_fscore_support(training_data_labels,
                                                torch.argmax(model_predictions, dim=1),
                                                zero_division=0,
                                                labels=(0,1,2,3,4))
        cost = cost_function(model_predictions, training_data_labels)
        writer.add_scalar('training loss', cost, count)
        for index, label in enumerate(f1):
                writer.add_scalar('training_label_'+str(index), label, count)
        cost.backward()
        gradient_descent.step()

writer.close()

print('Finished Training')
