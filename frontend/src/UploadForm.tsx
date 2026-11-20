interface UploadDeliveryProps{
    file:File|null
    setFile: React.Dispatch<React.SetStateAction<File|null>>
}
interface SaveDeliveryProps {
    file: File|null
}

async function SaveDelivery({file}:SaveDeliveryProps){
    const url = "http://localhost:8080/api/save";
    if (file == null){return "Video could not be saved"}
    try{
        const formData = new FormData()
        formData.append("video",file)
        const response = await fetch(url,{
            method:"POST",
            body:formData
        })
        const msg = await response.text();
        if (!response.ok){
            console.log(`Response message: ${response.status}, ${msg}`)
            return null;
        }
        console.log(msg);
        return msg;
    }catch(error){
        console.error(error)
        return null
    }
}

function UploadDelivery({file,setFile}:UploadDeliveryProps){
    return (
    <section id="upload">
        <div className="upload">
            <h2>Upload a delivery</h2>
            <label htmlFor="file">Upload a file: </label>
            <input type="file" id="file"
            onChange={(event)=>{
                const selected = event.target.files?.[0] ?? null
                setFile(selected)
                SaveDelivery({file:selected})
            }}/>
            <p>{file?.name ?? "No file selected"}</p>
        </div>
      </section>
    )
}

export default UploadDelivery