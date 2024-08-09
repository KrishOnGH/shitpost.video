from dotenv import load_dotenv
load_dotenv()
import praw
import os
import json
reddit = praw.Reddit(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    user_agent=os.getenv('user_agent'),
    username=os.getenv('redditusername'),
    password=os.getenv('password')
)

script_dir = os.path.dirname(os.path.abspath(__file__))

def fetch_from_link(link):
    try:
        # Fetch the submission from the link
        submission = reddit.submission(url=link)

        # Basic post info
        post_info = {
            'content': submission.selftext,
            'title': submission.title,
            'author': submission.author.name if submission.author else '[deleted]'
        }
        
        # Check the subreddit
        if submission.subreddit.display_name.lower() == "amitheasshole":
            return post_info
        
        elif submission.subreddit.display_name.lower() == "askreddit":
            # Sort comments by top and limit to 10
            submission.comment_sort = 'top'
            submission.comments.replace_more(limit=0)
            top_comments = submission.comments[:10]
            
            # Find the lengthiest comment among top 10
            longest_comment = max(top_comments, key=lambda c: len(c.body) if not isinstance(c, praw.models.MoreComments) else 0)
            
            post_info['top_comment'] = {
                'content': longest_comment.body,
                'author': longest_comment.author.name if longest_comment.author else '[deleted]',
                'score': longest_comment.score
            }
            
            return post_info
        
        else:
            return None
        
    except Exception as e:
        print(e)
        return None

def fetch_aita_post(username):
    # Get the subreddit
    subreddit = reddit.subreddit("AmItheAsshole")

    # Fetch top 30 and new 30 posts
    top_posts = list(subreddit.top(limit=30))
    new_posts = list(subreddit.new(limit=30))
    all_posts = top_posts + new_posts

    # Filter posts with content over 120 characters and title starting with AITA
    filtered_posts = [
        post for post in all_posts 
        if len(post.selftext) > 120 and post.title.lower().startswith("aita")
    ]

    # Load or create the used_posts.json file
    if os.path.exists(os.path.join(script_dir, 'used_posts.json')):
        with open(os.path.join(script_dir, 'used_posts.json'), 'r') as f:
            used_posts = json.load(f)
    else:
        used_posts = {}

    # Check if username exists in used_posts
    if username in used_posts:
        used_ids = set(used_posts[username])
        filtered_posts = [post for post in filtered_posts if post.id not in used_ids]
        if filtered_posts:
            used_posts[username].append(filtered_posts[0].id)
    else:
        used_posts[username] = [filtered_posts[0].id] if filtered_posts else []

    # Write back to used_posts.json
    with open(os.path.join(script_dir, 'used_posts.json'), 'w') as f:
        json.dump(used_posts, f)

    # Return the first post's details if available
    if filtered_posts:
        chosen_post = filtered_posts[0]
        return {
            'url': chosen_post.url,
            'content': chosen_post.selftext,
            'title': chosen_post.title,
            'author': chosen_post.author.name if chosen_post.author else '[deleted]'
        }
    else:
        return None

def fetch_askreddit_post(username):
    # Get the subreddit
    subreddit = reddit.subreddit("AskReddit")

    # Fetch top 30 and new 30 posts
    top_posts = list(subreddit.top(limit=30))
    new_posts = list(subreddit.new(limit=30))
    all_posts = top_posts + new_posts

    # Filter posts
    filtered_posts = [
        post for post in all_posts 
        if len(post.selftext) < 120 
        and post.title.endswith('?')
        and any(len(comment.body) > 120 for comment in post.comments if not isinstance(comment, praw.models.MoreComments))
    ]

    # Load or create the used_posts.json file
    if os.path.exists(os.path.join(script_dir, 'used_posts.json')):
        with open(os.path.join(script_dir, 'used_posts.json'), 'r') as f:
            used_posts = json.load(f)
    else:
        used_posts = {}

    # Check if username exists in used_posts
    if username in used_posts:
        used_ids = set(used_posts[username])
        filtered_posts = [post for post in filtered_posts if post.id not in used_ids]
        if filtered_posts:
            used_posts[username].append(filtered_posts[0].id)
            
    else:
        used_posts[username] = [filtered_posts[0].id] if filtered_posts else []

    # Write back to used_posts.json
    with open(os.path.join(script_dir, 'used_posts.json'), 'w') as f:
        json.dump(used_posts, f)

    # Return the first post's details if available
    if filtered_posts:
        chosen_post = filtered_posts[0]
        
        # Find the most upvoted comment over 120 characters
        chosen_post.comments.replace_more(limit=0)
        long_comments = [comment for comment in chosen_post.comments if len(comment.body) > 120]
        best_comment = max(long_comments, key=lambda c: c.score) if long_comments else None

        # Return post
        if best_comment:
            return {
                'url': chosen_post.url,
                'content': chosen_post.selftext,
                'title': chosen_post.title,
                'author': chosen_post.author.name if chosen_post.author else '[deleted]',
                'comment': {
                    'content': best_comment.body,
                    'author': best_comment.author.name if best_comment.author else '[deleted]',
                    'score': best_comment.score
                }
            }
        else:
            return None
    else:
        print('subreddit not found')
        return None