import csv

def process_csv(input_path, output_path):
    with open(input_path, 'r', newline='') as infile:
        reader = list(csv.reader(infile))
        header = reader[0]
        data = reader[1:]

    new_rows = []
    for i in range( len(data) - 1):
        row1 = data[i]
        row2 = data[i + 1]

        new_rows.append(row1)

        video_path = row1[0]
        label = row1[2]
        bbox = row1[3]

        time1 = float(row1[1])
        time2 = float(row2[1])
        new_time = (time1 + time2) / 2

        x1 = float(row1[4])
        x2 = float(row2[4])
        y1 = float(row1[5])
        y2 = float(row2[5])

        new_x = (x1 + x2) / 2
        new_y = (y1 + y2) / 2

        average_row = [video_path, new_time, label, bbox, new_x, new_y]
        new_rows.append(average_row)

    with open(output_path, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)
        writer.writerows(new_rows)

process_csv("giris.csv", "cikis.csv")
