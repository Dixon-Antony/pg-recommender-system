# from surprise import Dataset
# from surprise import Reader
# from surprise import SVD
# from surprise.model_selection import cross_validate

# # Load data
# reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5), skip_lines=1)
# data = Dataset.load_from_file('ratings.csv', reader=reader)

# # Use SVD algorithm
# algo = SVD()

# # Run 5-fold cross-validation and print results
# cross_validate(algo, data, measures=['RMSE'], cv=5, verbose=True)



from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
import os
from surprise import NMF

#------------------------load data from a file
reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5), skip_lines=1)
data = Dataset.load_from_file('testratings.csv', reader=reader)



from surprise import SVD
from surprise.model_selection import cross_validate
import os


#########---------------SVD
print('')
print('---------------SVD result-------------')
algo = SVD()
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)



#########---------------PMF
print('')
print('---------------PMF result--------------')
algo = SVD(biased=False)
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)


##########--------------NMF
print('')
print('----------------NMF result--------------')
algo = KNNBasic(sim_options = {'user_based':True})
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)



##########--------------User Based Collaborative Filtering algorithm
print('')
print('User Based Collaborative Filtering algorithm result')
algo = KNNBasic(sim_options = {'user_based': False })
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)





##########--------------Item Based Collaborative Filtering algorithm
print('')
print('Item Based Collaborative Filtering algorithm result')
algo = KNNBasic(sim_options = {'user_based': False})
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)



##########--------MSD------User Based Collaborative Filtering algorithm
print('')
print('MSD----User Based Collaborative Filtering algorithm result')
algo = KNNBasic(sim_options = {'name':'MSD','user_based': True})
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)



##########--------cosin------User Based Collaborative Filtering algorithm
print('')
print('cosin----User Based Collaborative Filtering algorithm result')
algo = KNNBasic(sim_options = {'name':'cosine','user_based': True})
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)


##########--------person------User Based Collaborative Filtering algorithm
print('')
print('Person sim----User Based Collaborative Filtering algorithm result')
algo = KNNBasic(sim_options = {'name':'pearson','user_based': True})
cross_validate(algo, data, measures=['RMSE', 'MAE'],cv=3,verbose=True)



##########--------MSD------User Based Collaborative Filtering algorithm
print('')
print('10--Neighboors--User Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':True })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------cosin------User Based Collaborative Filtering algorithm
print('')
print('10---Neighboors---Item Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':False })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------MSD------User Based Collaborative Filtering algorithm
print('')
print('15--Neighboors--User Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':True })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------cosin------User Based Collaborative Filtering algorithm
print('')
print('15---Neighboors---Item Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':False })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------MSD------User Based Collaborative Filtering algorithm
print('')
print('25--Neighboors--User Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':True })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------cosin------User Based Collaborative Filtering algorithm
print('')
print('25---Neighboors---Item Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':False })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)




##########--------MSD------User Based Collaborative Filtering algorithm
print('')
print('30--Neighboors--User Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':True })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)



##########--------cosin------User Based Collaborative Filtering algorithm
print('')
print('30---Neighboors---Item Based Collaborative Filtering algorithm result')
algo = KNNBasic(k=10, sim_options = {'name':'MSD', 'user_based':False })
cross_validate(algo, data, measures=['RMSE'],cv=3,verbose=True)




from surprise import Dataset, Reader, SVD, KNNBasic
from surprise.model_selection import train_test_split
from surprise.accuracy import rmse, mae


# Split the data into training and testing sets
trainset, testset = train_test_split(data, test_size=0.2)

# Define the SVD and k-NN algorithms
svd = SVD()
knn = KNNBasic()

# Fit each algorithm on the training set
svd.fit(trainset)
knn.fit(trainset)

# Use each algorithm to predict the ratings for the test set
svd_predictions = svd.test(testset)
knn_predictions = knn.test(testset)

# Evaluate the performance of each algorithm
svd_rmse = rmse(svd_predictions)
knn_rmse = rmse(knn_predictions)

svd_mae = mae(svd_predictions)
knn_mae = mae(knn_predictions)

# Print the results
print('SVD RMSE:', svd_rmse, 'MAE:', svd_mae)
print('k-NN RMSE:', knn_rmse, 'MAE:', knn_mae)
