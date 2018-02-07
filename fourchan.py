##4chan library

import requests, random

#post object. Content is basically the same as thread.
class post(object):
    def __init__(self,post_json,board=None,OP=None):
        self.post_json = post_json
        self.board = board
        try:
            self.subject = self.post_json["sub"]
        except KeyError:
            self.subject = None
        self.author = self.post_json["name"]
        try:
            self.file = "https://i.4cdn.org/"+self.board+"/"+str(self.post_json["tim"])+self.post_json["ext"]
            self.ext = self.post_json["ext"]
        except KeyError:
            self.file = None
            self.ext = None
        try:
            self.comment = self.post_json["com"]
        except:
            self.comment = None
        self.number = self.post_json["no"]
        self.link = OP.link+"#p"+str(self.number)

#thread object. Things get funky now. Represents a particular thread.
class thread(object):
    def __init__(self,thread_json,board=None,URL="https://a.4cdn.org"):
        self.thread_json = thread_json
        self.board = board
        self.__URL = URL
        self.__load()

    def __load(self): # Loading routine for extracting info from a thread
        try: # Fetch the subject
            self.subject = self.thread_json["posts"][0]["sub"]
        except KeyError:
            self.subject = None
        self.author = self.thread_json["posts"][0]["name"] # Name of the poster
        self.file = "https://i.4cdn.org/"+self.board+"/"+str(self.thread_json["posts"][0]["tim"])+self.thread_json["posts"][0]["ext"] # File URL + extension
        self.ext = self.thread_json["posts"][0]["ext"] # File extension
        try: # comment
            self.comment = self.thread_json["posts"][0]["com"]
        except KeyError:
            self.comment = None
        self.number = self.thread_json["posts"][0]["no"] # post number
        self.link = "https://boards.4chan.org/"+self.board+"/thread/"+str(self.number)
        self.get_detail()
        self.len = len(self.thread_json["posts"]) # length

    def __len__(self):
        return self.len

    def get_detail(self,board=None): # gets all posts in a thread
        if board==None:
            board = self.board
        r = requests.get(self.__URL+"/"+board+"/thread/"+str(self.number)+".json")
        self.thread_json = r.json()

    def __getitem__(self,i):
        return post(self.thread_json["posts"][i],self.board,self)

    def __iter__(self):
        for i in range(self.len):
            yield post(self.thread_json["posts"][i],self.board,self)

#board_page -- represents one page on a board
class board_page(object):
    def __init__(self,page_json,board=None):
        self.page_json = page_json
        self.board = board

    def __getitem__(self,i):
        return thread(self.page_json["threads"][i],self.board)

    def __len__(self):
        return len(self.page_json["threads"])

#chan object. Starting place of the code.
class chan(object):
    def __init__(self,URL="https://a.4cdn.org"):
        self.URL = URL
        self.s = requests.session()

    def loadBoard(self,board,page=1):
        r = self.s.get(self.URL+"/"+board+"/"+str(page)+".json") # Get from the api the contents of that page on that board
        return board_page(r.json(),board)

    def randomFile(self,board,extensions=[".jpg", ".png", ".gif", ".pdf", ".swf", ".webm"],**kwargs):
        if not kwargs.has_key("post_link"):
            post_link = False
        else:
            post_link = kwargs["post_link"]
        b = self.loadBoard(board,random.randrange(0,11)) # Loads a random page of the board
        t = b[random.randrange(0,len(b))] # Picks a random thread from the page
        files = filter(lambda p:(p.ext in extensions),[p for p in t if p.file != None]) # Gets all posts with files, and filters by extension
        post = files[random.randrange(0,len(files))]
        if not post_link:
            return post.file # Returns the URL of a random file from the thread
        if post_link:
            return (post.file,post.link)

