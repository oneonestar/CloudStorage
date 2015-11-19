package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	//"io/ioutil"
	"net/http"
)

type response_upload struct {
	Status bool `json:"status"`
	Message string `json:"message"`
}

func _client_upload_fail(w http.ResponseWriter, r *http.Request, message string) {
	ret := &response_upload {
		Status: false,
		Message: message}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func _client_upload_success(w http.ResponseWriter, r *http.Request) {
	ret := &response_upload {
		Status: true,
		Message: "success"}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func client_upload(w http.ResponseWriter, r *http.Request) {
	// Retrieve token from request
	r.ParseMultipartForm(32 << 20)
	token_arr, ok := r.Form["token"]
	if !ok {
		fmt.Println("FAILED to get token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	}
	token := token_arr[0]
	fmt.Println(token)

	// Verify token
	client_id, ok := verify_token(token)
	if !ok {
		fmt.Println("Invalid token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	}

	// Upload file
	file, handler, err := r.FormFile("document")
	if err != nil {
		fmt.Println(err)
		return
	}
	defer file.Close()
	fmt.Println("Filename: "+handler.Filename)
	f, err := os.OpenFile("data/"+client_id+"-"+handler.Filename, os.O_WRONLY|os.O_CREATE, 0666)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()
	io.Copy(f, file)
	//fmt.Fprintf(w, "Hi there, I love %s!", r.URL.Path[1:])
	_client_upload_success(w, r)
}
