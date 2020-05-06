#!/usr/bin/python3
# simple testing program opening a feedback file


fb = [
         '[animal]cat',
         '[animal]dog',
         '# This is a comment line followed by 2 empty lines',
         '',
         '',
         '[person]joe',
         '[town]London',
         '[town]Paris',
         '[date_unix]1588791309',
         '[date_long]Wed 06 May 2020 08:56:15 PM CEST',
         '[jsample]{ "items" : { "item1" : "suitcase", "item2" : "umbrella"} }',
         '[progress]36',
         '[progress]50',
         '[progress]60',
         '[name]=Paul Emile Victor de la Petaudiere'
     ]


f = open("feedback.log","w")
for line in fb:
    f.write(line)
    f.write("\n")
f.close



