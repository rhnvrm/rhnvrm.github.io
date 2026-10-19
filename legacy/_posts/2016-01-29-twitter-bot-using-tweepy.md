---
layout: post
title: Twitter bots using Tweepy
---

![twitter](http://naldzgraphics.net/wp-content/uploads/2009/04/twi1.jpg)

Unable to think what to tweet about? Have you ever faced a similar situation?

Well, it's very easy to create your own bots using python's Tweepy module. You can use these skeletons I recently made for a workshop on the same topic. All you need to make your own bot is add some logic to these skeletons.

---

This is a basic static script that you can use by running once yourself or setup a cronjob to run automaticall in intervals. Currently, it fetches JSON data from an API and parses it into a python dict which you can then manipulate with your py-fu.

<script src="https://gist-it.appspot.com/github.com/ACM-SNU/api-bot-python/blob/master/samples/static_programming_contest.py"></script>

---

This script uses twitter's streaming API which you can use to read content in real time and act upon it again, in real time!

<script src="https://gist-it.appspot.com/github.com/ACM-SNU/api-bot-python/blob/master/samples/stream_and_reply.py"></script>

---

Note you will also need this file in the same directory, it holds your keys. You should add this file to `.gitignore` before commiting your keys in your own repo.

<script src="https://gist-it.appspot.com/github.com/ACM-SNU/api-bot-python/blob/master/samples/key.py"></script>


If you create your own bot using this, we would love for you to also add it to the [audience](https://github.com/ACM-SNU/api-bot-python/tree/master/audience) folder in the repo by sending a pull request.