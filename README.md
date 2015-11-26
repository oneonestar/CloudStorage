# CloudStorage
Secure Cloud Storage System

## Install
### Debian / Ubuntu
```
sudo apt-get install python3-dev libffi-dev python3-pip libffi-dev libssl-dev python3-bson
sudo pip3 install cffi --upgrade
sudo pip3 install cryptography ldap3
sudo pip3 install https://github.com/ricmoo/pyscrypt/archive/master.zip
sudo apt-get install golang
```

### GO
```
cd src/server
export GOPATH=`pwd`
go get golang.org/x/crypto/scrypt
```

## Execute
### Server side
```
cd src/server
./run.sh
```

### Client side
```
cd src/client
./run.sh
```



# Testing
## RSA (E-cert)
Convert e-cert .p12 file to pem
```
openssl pkcs12 -in path.p12 -out newfile.crt.pem -clcerts -nokeys
openssl pkcs12 -in path.p12 -out newfile.key.pem -nocerts -nodes
```

Decrypt
```
openssl rsautl -in enc -inkey me.key.pem -decrypt -oaep -hexdump
```
