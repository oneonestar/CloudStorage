package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

type response_delete struct {
	Status  bool   `json:"status"`
	Message string `json:"message"`
}

// Return a json message to client indicate the download failed
func _client_delete_fail(w http.ResponseWriter, r *http.Request, message string) {
	ret := &response_delete{
		Status:  false,
		Message: message}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func _client_delete_success(w http.ResponseWriter, r *http.Request) {
	ret := &response_upload{
		Status:  true,
		Message: "success"}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func client_delete(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()

	var filename string
	//Retrieve filename
	if filename_arr, ok := r.Form["file"]; !ok {
		fmt.Println("FAILED to get filename")
		_client_upload_fail(w, r, "Invalid filename")
		return
	} else {
		filename = filename_arr[0]
	}

	var token string
	// Retrieve token
	if token_arr, ok := r.Form["token"]; !ok {
		fmt.Println("FAILED to get token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	} else {
		token = token_arr[0]
	}

	// Verify token
	client_id, ok := verify_token(token)
	if !ok {
		fmt.Println("Invalid token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	}

	fmt.Println("data/" + client_id + "-" + filename)
	os.Remove("data/" + client_id + "-" + filename)
	_client_delete_success(w, r)
}
