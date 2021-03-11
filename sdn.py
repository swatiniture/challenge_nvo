try:
    from flask import Flask, render_template, redirect, request
    import subprocess
    import sys
except ImportError as e:
    print ("Please install required modules! Exiting..!")
    sys.exit(0)

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/sdndata", methods=["GET", "POST"])
def sdndata():

    if request.method == "POST":
        req = request.form

        src = req.get("src")
        dst = req.get("dst")
        dstport = req.get("dstport")

        print (src)
        print (dst)
        print (dstport)

    return render_template('sdndata.html', title='SDN Longest Path', src=src, dst=dst, dstport=dstport)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
