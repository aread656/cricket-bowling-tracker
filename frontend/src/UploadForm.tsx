import {useState} from "react"
function UploadDelivery(){
    const [file,setFile] = useState<File|null>(null)
    return (
    <section id="analyse">
        <div className="analyse">
            <h2>Upload a delivery</h2>
            <label htmlFor="file">Upload a file: </label>
            <input type="file" id="file"
            onChange={(event)=>{
                setFile(event.target.files?.[0] ?? null)
            }}/>
            <p>{file?.name ?? "No file selected"}</p>
            <button type="button">Analyse Video</button>
        </div>
      </section>
    )
}
export default UploadDelivery