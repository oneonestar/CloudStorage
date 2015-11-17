package main

import (
	//"encoding/json"
	"fmt"
	"io"
	"os"
	//"io/ioutil"
	"net/http"
)

type test_struct struct {
	Test string
}

func client_upload(w http.ResponseWriter, r *http.Request) {
	fmt.Println(r.Form["filename"])
	file, handler, err := r.FormFile("document")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close()
	fmt.Fprintf(w, "%v", handler.Header)
	f, err := os.OpenFile(handler.Filename, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()
	io.Copy(f, file)
	//fmt.Fprintf(w, "Hi there, I love %s!", r.URL.Path[1:])
	fmt.Fprintf(w, "Success")
}

func client_download(w http.ResponseWriter, r *http.Request) {
	filename := r.Form["filename"][0]
	fmt.Println(filename)
	http.ServeFile(w, r, filename)
}

func handler(w http.ResponseWriter, r *http.Request) {
	r.ParseMultipartForm(32 << 20)
	cmd := r.Form["command"][0]
	fmt.Println(cmd)
	if cmd == "upload" {
		client_upload(w, r)
	} else if cmd == "download" {
		client_download(w, r)
	}
	//fmt.Println(r)
	/*
		fmt.Println(r.FormValue("myinfo"))
		fmt.Println(r.FormValue("document"))
		fmt.Println(r.Form)
		fmt.Println("scheme", r.URL)
		fmt.Println("scheme", r.URL.Path)
		fmt.Println(r.Form["url_long"])
		fmt.Println("scheme", r.URL.Scheme)
		//str := r.FormValue("myinfo2")
		str := r.FormValue("files")
		fmt.Println(str)*/
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServeTLS(":8080","server.pem", "server.key", nil)
}
