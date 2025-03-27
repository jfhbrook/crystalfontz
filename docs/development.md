# Development

I use `uv` for managing dependencies, but also compile `requirements.txt` and `requirements_dev.txt` files that one can use instead. I also use `just` for task running, but if you don't have it installed you can run the commands manually.

There *are* some unit tests in `pytest`, but they mostly target more complex cases of marshalling/unmarshalling and calculating packet CRCs. The bulk of testing involves setting up `crystalfontz` on the computer that has the CFA533, running the `./tests/integration.sh` script, and seeing what it does.

## Issues

There is a *really* long tail of things that I'd like to tackle for this library. Most of those things are captured in [GitHub Issues](https://github.com/jfhbrook/crystalfontz/issues).
