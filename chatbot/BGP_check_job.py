import os

# All run() must be inside a main function
def main(runtime):
    # Find the location of the script in relation to the job file
    bgp_tests = os.path.join(os.path.dirname(__file__), 
                             'BGP_Neighbors_Established.py')
    # Execute the testscript
    runtime.tasks.run(testscript=testbed/routers)
