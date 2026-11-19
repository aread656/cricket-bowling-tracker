interface UploadDeliveryProps{
    file:File|null
    setFile: React.Dispatch<React.SetStateAction<File|null>>
}
function UploadDelivery({file,setFile}:UploadDeliveryProps){
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
        </div>
      </section>
    )
}
export default UploadDelivery