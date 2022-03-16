# pacu3

Previously I was using the [pacu2](https://github.com/RyanJarv/pacu2) repo as a scratch space for testing potential features for a future rewrite
of pacu. That's all too messy for any real use during the rewrite though.

The next step in the process is figuring out what modules should be kept and what the overall structure should look like then writing basic tests
for what needs to be worked on. I'm hoping to use this repo for that.

## Thoughts

Right now pacu (and pacu2) has a lot of stuff going on of questionable use which makes it difficult to understand and maintain. For the purposes of
the rewrite right now, I wanted to remove everything that isn't absolutely needed so we can focus on the "modules".

With that in mind, there is no REPL here, everything just works through imports, and their should be minimal code for the moment (at least until
we can understand what this will all contain).
