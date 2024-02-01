class Evaluate:
    def __init__(self, instructions):
        self.instructions = instructions
        
    def run(self):
        # You can now use self.input_schema in this method
        return self.instructions
    
    # check if {variable_1}, {variable_2} etc are present in instructions, if so, swap them for values in csv. if not, run the function again
