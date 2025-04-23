# import locust
# from locust import HttpUser, TaskSet, task, between
# import random
# import json

# class UserBehavior(TaskSet):
#     def on_start(self):
#         """Simulate user creation and login to obtain JWT token."""
#         # Generate a unique email for each user
#         unique_email = f"user{random.randint(1000, 9999)}@example.com"
#         password = "password123"

#         # Step 1: Create a user
#         create_user_response = self.client.post(
#             "/user/register",
#             json={
#                 "email": unique_email,
#                 "name": "Test User",
#                 "password": password,
#                 "confirmPassword": password
#             }
#         )

#         if create_user_response.status_code == 200:
#             # Step 2: Sign in with the created user to obtain JWT token
#             sign_in_response = self.client.post(
#                 "/user/signIn",
#                 json={"email": unique_email, "password": password}
#             )
#             if sign_in_response.status_code == 200:
#                 self.jwt_token = sign_in_response.json().get("token")
#             else:
#                 self.jwt_token = None
#                 # print(f"Sign-in failed: {sign_in_response.text}")
#         else:
#             self.jwt_token = None
#             # print(f"User creation failed: {create_user_response.text}")

            
#         @task(3)  # Weight: 3 (more frequent)
#         def get_trending_movies(self):
#             """Simulate a GET request to fetch trending movies."""
#             self.client.get(
#                 "/user/trendingMovies",
#                 headers={"token": self.jwt_token}
#             )

# #     @task(2)  # Weight: 2
# #     def search_item(self):
# #         """Simulate a GET request to search for a movie."""
# #         query = random.choice(["action", "comedy", "drama"])
# #         self.client.get(
# #             f"/user/searchItem?name={query}",
# #             headers={"token": self.jwt_token}
# #         )

# #     @task(1)  # Weight: 1 (less frequent)
# #     def update_password(self):
# #         """Simulate a POST request to update the password."""
# #         self.client.post(
# #             "/user/updatePassword",
# #             headers={"token": self.jwt_token},
# #             json={"password": "newpassword123", "confirmPassword": "newpassword123"}
# #         )

# #     @task(2)  # Weight: 2
# #     def get_genre_list(self):
# #         """Simulate a GET request to fetch genre list."""
# #         self.client.get(
# #             "/user/genreList",
# #             headers={"token": self.jwt_token}
# #         )

# #     @task(1)  # Weight: 1
# #     def create_user(self):
# #         """Simulate a POST request to create a new user."""
# #         self.client.post(
# #             "/user/register",
# #             json={
# #                 "email": f"user{random.randint(1000, 9999)}@example.com",
# #                 "name": "Test User",
# #                 "password": "password123",
# #                 "confirmPassword": "password123"
# #             }
# #         )

# class WebsiteUser(HttpUser):
#     tasks = [UserBehavior]
#     wait_time = between(1, 5)  # Simulate a wait time between requests (1-5 seconds)
#     host = "http://localhost:8000/"


from locust import HttpUser, TaskSet, task, between
import random

class UserBehavior(TaskSet):
    def on_start(self):
        unique_email = f"user{random.randint(1000, 9999)}@example.com"
        password = "password123"

        create_user_response = self.client.post(
            "/user/register",
            json={
                "email": unique_email,
                "name": "Test User",
                "password": password,
                "confirmPassword": password
            }
        )

        if create_user_response.status_code == 200:
            sign_in_response = self.client.post(
                "/user/signIn",
                json={"email": unique_email, "password": password}
            )
            if sign_in_response.status_code == 200:
                self.jwt_token = sign_in_response.json().get("token")
            else:
                self.jwt_token = None
        else:
            self.jwt_token = None

    @task(2)
    def get_trending_movies(self):
        if self.jwt_token:
            self.client.get(
                "/user/trendingMovies",
                headers={"token": self.jwt_token}
            )
    @task(2)
    def test_genreList(self):
        if self.jwt_token:
            self.client.get(
                "/user/genreList",
                headers={"token": self.jwt_token}
            )
    # @task(3)
    # def test_genreSelector(self):
        
    # @task(3)
    # def test_languageList(self):
        
    # @task(3)
    # def test_languageSelector(self):
        
    # @task(3)
    # def test_trendingMovies(self):
    
    # @task(3)
    # def test_trendingTrailers(self):
    
    # @task(3)
    # def test_getUserDetails(self):

    # @task(3)
    # def test_searchItem(self):
    
    # @task(3)
    # def test_checkInTask(self):
    
    # @task(3)
    # def test_collectCheckIn(self):
    
    # @task(3)
    # def test_markBookMark(self):
    
    # @task(3)
    # def test_getBookMark(self):
    
    # @task(3)
    # def test_likeVideo(self):
    
    # @task(3)
    # def test_getAds(self):
    
    # @task(3)
    # def test_(self):
    
    # @task(3)
    # def test_getPackage(self):
    
    # @task(3)
    # def test_googleAuth(self):

    # @task(3)
    # def test_fetchWallet(self):
    
    # @task(3)
    # def test_forgotPassword(self):
    
    # @task(3)
    # def test_verifyOtp(self):
    
    # @task(3)
    # def test_updatePassword(self):
    
    # @task(3)
    # def test_mintsPurchaseHistory(self):

    # @task(3)
    # def test_continueWatching(self):
    
    # @task(3)
    # def test_getContinueWatching(self):
    
    # @task(3)
    # def test_unlikeVideo(self):

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  
    host = "http://localhost:8000/"

# locust -f core/load_test.py