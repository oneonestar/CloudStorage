package main

import (
	"encoding/json"
	"encoding/gob"
	"fmt"
	"os"
	//"io/ioutil"
	"net/http"
)

// ===========================================
// Share db
type share_record struct {
	Sender string
	Record string
}
var share_db map[string]([]share_record)
// ===========================================
func share_setup() {
	if share_db == nil {
		share_db = make(map[string]([]share_record))
	}
}

func share_save_db() {
	filename := "share_db"
	f, err := os.Create(filename)
	if err != nil {
		panic("cant open file")
	}
	defer f.Close()

	enc := gob.NewEncoder(f)
	if err := enc.Encode(share_db); err != nil {
		panic("cant encode")
	}
}

func share_load_db() {
	filename := "share_db"
	f, err := os.Open(filename)
	if err != nil {
		fmt.Println("Cannot load db file")
		return
	}
	defer f.Close()

	enc := gob.NewDecoder(f)
	if err := enc.Decode(&share_db); err != nil {
		panic("cant decode")
	}
}
type response_share struct {
	Status  bool   `json:"status"`
	Message string `json:"message"`
}
type response_share_list struct {
	Status  bool   `json:"status"`
	Records []share_record `json:"records"`
}

func _client_share_fail(w http.ResponseWriter, r *http.Request, message string) {
	ret := &response_share{
		Status:  false,
		Message: message}
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}

func _client_share_success(w http.ResponseWriter, r *http.Request) {
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

func client_share_list(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()

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

	var ret response_share_list
	fmt.Println(share_db)
	ret.Status = true;
	ret.Records = share_db[client_id];
	ret2, err := json.Marshal(ret)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprintf(w, string(ret2))
	fmt.Println("Response: ", string(ret2))
}


func client_share(w http.ResponseWriter, r *http.Request) {
	// Retrieve token from request
	r.ParseMultipartForm(32 << 20)
	var token string
	if token_arr, ok := r.Form["token"]; !ok {
		fmt.Println("FAILED to get token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	} else {
		token = token_arr[0]
	}
	fmt.Println(token)

	// Verify token
	var client_id string
	if id, ok := verify_token(token); !ok {
		fmt.Println("Invalid token")
		_client_upload_fail(w, r, "Invalid Token")
		return
	} else {
		client_id = id
	}

	var recipient string
	if recipient_arr, ok := r.Form["recipient"]; !ok {
		fmt.Println("FAILED to recipient")
		_client_upload_fail(w, r, "Invalid Recipient")
		return
	} else {
		recipient = recipient_arr[0]
	}

	var data string
	if data_arr, ok := r.Form["data"]; !ok {
		fmt.Println("FAILED to recipient")
		_client_upload_fail(w, r, "Invalid Recipient")
		return
	} else {
		data = data_arr[0]
	}
	fmt.Println(client_id)
	fmt.Println(recipient)
	fmt.Println(data)

	share_db[recipient] = append(share_db[recipient], share_record{
					Sender: client_id,
					Record: data})

	_client_upload_success(w, r)
	fmt.Println(share_db)
}
