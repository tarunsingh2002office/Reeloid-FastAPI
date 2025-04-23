from locust import HttpUser, TaskSet, task, between
import random
import string

class UserBehavior(TaskSet):
    allGenreIDs = ["670f5038b6a595b05f97336e","670f55b6b6a595b05f973398","670f5092b6a595b05f973374","670f5065b6a595b05f973372","670f5051b6a595b05f973370"]
    allLanguageIDs = ["6756daf4ff91008fc67fa749","670f50a4b6a595b05f97337b","670f509eb6a595b05f973379","670f509ab6a595b05f973377"]

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

    @task(3)
    def test_genreSelector(self):
        count = random.randint(1, len(self.allGenreIDs))
        randomGenresSelected = random.sample(self.allGenreIDs, k=count)
        self.client.post(
            "/user/genreSelection",
            headers={"token": self.jwt_token},
            json={"selectedGenre": randomGenresSelected}
        )

    @task(2)
    def test_languageList(self):
        if self.jwt_token:
            self.client.get(
                "/user/languageList",
                headers={"token": self.jwt_token}
            )

    @task(3)
    def test_languageSelector(self):
        count = random.randint(1, len(self.allLanguageIDs))
        randomLanguageSelected = random.sample(self.allLanguageIDs, k=count)
        self.client.post(
            "/user/languageSelector",
            headers={"token": self.jwt_token},
            json={"selectedGenre": randomLanguageSelected}
        )
        
    @task(2)
    def test_trendingMovies(self):
        if self.jwt_token:
            self.client.get(
                "/user/trendingMovies",
                headers={"token": self.jwt_token}
            )
    
    @task(2)
    def test_trendingTrailers(self):
        if self.jwt_token:
            self.client.get(
                "/user/trendingTrailers",
                headers={"token": self.jwt_token}
            )

    @task(2)
    def test_getUserDetails(self):
        if self.jwt_token:
            self.client.get(
                "/user/getUserDetails",
                headers={"token": self.jwt_token}
            )

    @task(3)
    def test_editUserDetails(self):
        self.client.post(
            "/user/editUserDetails",
            headers={"token": self.jwt_token},
            json={
                "email": "updated@gmail.com",
                "name": "Test User",
                "password": "password1234",
                "confirmPassword": "password123"
            }
        )

    @task(2)
    def test_searchItem(self):
        search_query = ''.join(random.choices(string.ascii_lowercase, k=2))
        self.client.get(
            "/user/searchItem",
            params={"name": search_query},
            headers={"token": self.jwt_token}
        )
    
    @task(3)
    def test_checkInTask(self):
        self.client.post(
            "/user/checkInTask",
            headers={"token": self.jwt_token},
        )
    
    @task(3)
    def test_collectCheckIn(self):
    
    @task(3)
    def test_markBookMark(self):
    
    @task(2)
    def test_getBookMark(self):
    
    @task(3)
    def test_likeVideo(self):
    
    @task(2)
    def test_getAds(self):
    
    @task(2)
    def test_getPackage(self):

    @task(2)
    def test_fetchWallet(self):
    
    @task(3)
    def test_forgotPassword(self):
    
    @task(2)
    def test_mintsPurchaseHistory(self):

    @task(3)
    def test_continueWatching(self):
    
    @task(2)
    def test_getContinueWatching(self):
    
    @task(3)
    def test_unlikeVideo(self):

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)  
    host = "http://localhost:8000/"

# locust -f core/load_test.py