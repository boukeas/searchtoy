import argparse

parser = argparse.ArgumentParser(description="Converts sudoku batch files (norvig-style) to separate grid files.")

parser.add_argument('-f', '--filename', required=True,
                    help='the name of the file containing the puzzle')

settings = parser.parse_args()

with open(settings.filename) as infile:
    
    for lineno, puzzle in enumerate(infile, start=1):
        
        converted_puzzle = "\n".join([puzzle[linestart:linestart+9] for linestart in range(0, 81, 9)])
        print("[" + str(lineno) + "]")
        print(converted_puzzle) 
        with open(settings.filename + "." + str(lineno), "w+") as outfile:
            outfile.write(converted_puzzle)

