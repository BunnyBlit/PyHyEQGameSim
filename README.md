# It's a Hybrid Equations Video Game Simulator / Analyzer!

For simple action games! Hopefully! It's a big work in progress.

✨ I am not maintaining this in the usual sense-- it's a hobby project that you can clone / take a look at! If you want to add in a feature, clone it and go wild, but please don't request it. I won't add it in. I make no promises about it running on your machine or my timeline to fix bugs.✨

This repository is a Python implementation of [Analyzing Action Games: A Hybrid Systems Approach](https://dl.acm.org/doi/pdf/10.1145/3337722.3337757). Currently the only game I have a model for is Flappy Bird, so I hope you're into a mid-aughts mobile game hit. I'm not 100% sure it's correct yet, some lower bounds still look pretty suspicious to me.

To Do Some Stuff With Flappy, Use:
```console
# download and install requirements
# (matplotlib for graphs, scipy for ODE solving, tqdm isn't needed but helps my sanity with dev work)
$ pip install -r requirements.txt

# for a single run on a generated level
$ python3 cli.py --sample_rate 0.02 single --samples 0 0 0 1 1 1 

# for a reachability analysis on a generated level
$ python3 cli.py --sample_rate 0.02 reachability --num_samples 20
```

Some cases can run really slowly-- it can take up to 15 minutes to get 1 second of game play sometimes :c. 

Blog Post Pending on What Is Going On Here and Why You Might Care