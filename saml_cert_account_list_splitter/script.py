# dirty little script to help me split a data dump of 3000+ rows in a CSV file
# to multiple files with 200 rows each. 
# just works! 

import csv

# open the primary data file here
with open('data.csv') as data:
    reader = csv.reader(data);
    
    # grab the field names in the variable. We will need to insert this
    # fieldname in all the new data output files we create
    fieldnames = next(reader)

    # maintain a count to grab 200 rows in one output file
    row_count,file_count = 0,0

    for row in reader:
        row_count = row_count + 1

        filename = 'data_{}.csv'.format(file_count)

        # change the output file name and insert the initial fieldnames
        # header
        if row_count%200 == 0:
            file_count = file_count + 1
            filename = 'data_{}.csv'.format(file_count)
            print('Writing data to file: {}'.format(filename))
            with open(filename,'w') as output0:
                writer = csv.writer(output0)
                writer.writerow(fieldnames)

        # dump rows to the output file
        with open(filename,'a') as output1:
            writer = csv.writer(output1)
            # had to add this if condition to insert the fieldnames header to the first
            # data file only
            if row_count == 1:
                writer.writerow(fieldnames)
            writer.writerow(row)
