## What's Next
1. Feasibility: as the inverse of reachability, this might be a better thing to port to other systems
* * Time to actually implement the feasibility algorithm, I think I have it ported to handling input
* * May need to rewrite parts of the underlying solver again: I get the nearest sim-step to a jump. I need the _exact_ time of a jump, even if this has me no longer evenly sample the space
2. Cleanup code for Github + Readme
3. Take another stab at CSV-file based serialization / deserialization of sims
4. Take start state from config file or CLI
5. Take system params from config file or CLI