from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import os
import re
import sys

if len(sys.argv) < 2:
    print("USAGE: {} domain.tld".format(sys.argv[0]))
    exit(-1)


class Scraper(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.scraped_domain: str = sys.argv[1]
        super().__init__(request, client_address, server)

    def scrape(self, request: str):

        url = 'https://{d}/{r}'.format(d = self.scraped_domain, r = request)
        
        print("\tScraping {}".format(url))
        
        response = requests.get(url)

        print("\tResponse: {}".format(response.status_code))
        
        tokens = self.get_local_path_tokens(request)
        path = self.get_path(tokens)
        file = self.get_filename(tokens)

        print("\tStoring: {p}/{f}".format(p = path, f = file))

        os.system("mkdir -p {p}".format(p = path))
        f = open("{p}/{f}".format(p = path, f = file), "wb")
        f.write(response.content)
        f.close()

    def get_local_path_tokens(self, request: str):
        tokens = re.split('/', request);
        
        if re.search("\\.", tokens[::-1][0]) == None:
            tokens.append("index.html")

        # domain.tld/path?_rsc=... - afaik its nextjs prefetching
        for i in range(len(tokens)):
            tokens[i] = re.sub("(\\?_.*)", "", tokens[i])

        return tokens
        

    def get_path(self, tokens: list[str]):
        final_string: str = "output/" + self.scraped_domain
        
        for x in tokens:
            if re.search("\\.", x) == None:
                final_string += '/' + x 
            
        return final_string

    def get_filename(self, tokens: list[str]):

        for x in tokens:
            if re.search("\\.", x) != None:
                return x
        
        return ""


    def do_GET(self):
        while True:
            try:        
                tokens = self.get_local_path_tokens(self.path[1:])
                path = self.get_path(tokens)
                file = self.get_filename(tokens)

                data = open("{p}/{f}".format(p = path, f = file), "rb").read()
            except:
                self.scrape(self.path[1:])

            else:
                self.send_response(200)
                break
            
        self.end_headers()
        
        self.wfile.write(data)

httpd = HTTPServer(('localhost',8080),Scraper)

print("Starting Server on http://localhost:8080")


httpd.serve_forever()