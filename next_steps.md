## What's Next
1. Feasibility: as the inverse of reachability, this might be a better thing to port to other systems
* * Time to actually implement the feasibility algorithm, I think I have it ported to handling input
* * May need to rewrite parts of the underlying solver again: I get the nearest sim-step to a jump. I need the _exact_ time of a jump, even if this has me no longer evenly sample the space
* * * this isn't possible with scipy's `solve_ivp` I don't think. Stuff to add for when I write my own in Rust!
* * As it stands, going backwards will always have an initial value problem-- for flappers, we can't disambiguate between if the initial velocity starting a fall was 2 or the start state velocity,
we don't know when we started!
* * * we could provide like a window of sorts, doing something like local vs world time
2. Cleanup code for Github + Readme
3. Take another stab at CSV-file based serialization / deserialization of sims
4. Take start state from config file or CLI
5. Take system params from config file or CLI