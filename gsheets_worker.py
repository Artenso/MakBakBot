import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
import gspread


class GSheetsWorker:

    def __init__(self, jsonkey_file_name):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            jsonkey_file_name, ['https://www.googleapis.com/auth/spreadsheets',
                                'https://www.googleapis.com/auth/drive']
        )
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build(
            'sheets', 'v4', http=self.httpAuth
        )
        self.client = gspread.authorize(self.credentials)

    def insert_to_table(self, spreadsheet_id, cell_range, information):

        self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=cell_range,
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
            body={"values": [information]}).execute()

    def insert_data_to_blank(self, spreadsheet_id, information):
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [{
                    "range": "D4:D16",
                    "majorDimension": "COLUMNS",
                    "values": [information]
                }]
            }
        ).execute()

    def insert_string_data_to_blank(self, spreadsheet_id, information):
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "A23:O23",
                     "majorDimension": "ROWS",
                     "values": [information]}]}).execute()

    def insert_delivery_data_to_blank(self, spreadsheet_id, information):
        self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "valueInputOption": "USER_ENTERED",
                "data": [
                    {"range": "A26:O26",
                     "majorDimension": "ROWS",
                     "values": [information]}]}).execute()

    def read_from_delivery_table(self, spreadsheet_id, spreadsheet_name, date):
        read_range = self.client.open(spreadsheet_name).sheet1.findall(
            date, in_column=1)
        read_range = str(read_range).replace(
            '<Cell R', ''
        ).replace(
            f"C1 '{date}'>", ''
        ).replace(
            '[', ''
        ).replace(
            ',', ''
        ).replace(
            ']', ''
        ).split(' ')
        range_low = read_range[0]
        range_high = read_range[len(read_range) - 1]

        if read_range != ['']:
            values = self.service.spreadsheets().values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=[f'A{range_low}:N{range_high}'],
                majorDimension='ROWS',
            ).execute()
            values = str(values['valueRanges'])
            values = values.replace(
                f''''range': "'Лист1'!{
                values[values.find('!') + 1:values.find('", ')]
                }", 'majorDimension': 'ROWS', 'values':''', '')
        else:

            values = 'На завтра доставок нет'

        return values
