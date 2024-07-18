import praw

reddit = praw.Reddit(
    client_id="KMoMAAdBSVqXiC2rvdV1pQ",
    client_secret="gVzz2l6eVrLYD68nBqYGxqSlMCZldQ",
    user_agent="shitpost by u/CalligrapherFun8155",
    username="CalligrapherFun8155",
    password="idontwannatalkonnocelly"
)

subreddit = reddit.subreddit("AmItheAsshole")
top_posts = subreddit.top(limit=10)
new_posts = subreddit.new(limit=10)

for post in top_posts:
    print(post.title)
    print(post.id)
    print(post.author)
    print(post.url)
    print(post.score)
    print(post.num_comments)
    print(post.created_utc)
    print("\n")
