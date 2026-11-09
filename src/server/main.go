package main

import ("net/http";"log";"fmt";"os";"io";"path/filepath")

func get_video(w http.ResponseWriter, r *http.Request){
	file, header, err := r.FormFile("video")
	w.Header().Set("Context-Type","text/plain")
	if err != nil{
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w,"Error: %v",err)
		return
	}
	header.Filename = filepath.Base(header.Filename)
	defer file.Close()
	fmt.Fprintf(w,"File: %s, Size: %d", header.Filename,header.Size)
	w.WriteHeader(http.StatusOK)
}

func save_video(w http.ResponseWriter, r *http.Request){
	w.Header().Set("Content-Type", "text/plain")
	src, header, err := r.FormFile("video")
	if err != nil{
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w,"Error: %v", err)
		return
	}
	header.Filename = filepath.Base(header.Filename)
	defer src.Close()

	path := filepath.Join("uploads/", header.Filename)
	dst, err := os.Create(path)
	if err != nil{
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w,"Error: %v", err)
		return
	}
	defer dst.Close()
	
	size, err := io.Copy(dst, src)
	if err != nil{
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w,"Error: %v",err)
		os.Remove(path)
		return
	}
	if size != header.Size{
		w.WriteHeader(http.StatusBadRequest)
		fmt.Fprintf(w,"Error: %v",err)
		os.Remove(path)
		return
	}
	w.WriteHeader(http.StatusOK)
	fmt.Fprintf(w,"File %v has been saved", header.Filename)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/healthz", func(w http.ResponseWriter, r *http.Request){
		w.Write([]byte("Server is running"))
	})
	mux.HandleFunc("POST /api/videos", get_video)
	mux.HandleFunc("POST /api/save", save_video)
	log.Fatal(http.ListenAndServe(":8081",mux))
}