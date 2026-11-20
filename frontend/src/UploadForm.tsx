import {useState} from "react"

interface UploadDeliveryProps{
    file:File|null
    setFile: React.Dispatch<React.SetStateAction<File|null>>
}
interface SaveDeliveryProps {
    file: File|null
    session: string
    onSaved: (upload: {filename:string; session:string}|null) => void
}

async function SaveDelivery({file,session,onSaved}:SaveDeliveryProps){
    const url = "http://localhost:8080/api/save";
    if (file == null){onSaved(null); return}
    try{
        const formData = new FormData()
        formData.append("video",file,file.name)
        formData.append("session",session)
        const response = await fetch(url,{
            method:"POST",
            body:formData
        })
        const msg = await response.text();
        if (!response.ok){
            console.log(`Response message: ${response.status}, ${msg}`)
            onSaved(null); return null;
        }
        const upload = JSON.parse(msg) as {filename:string;session:string}
        onSaved(upload)
        console.log("Saved video: "+upload.session+"/"+upload.filename)
        return upload;
    }catch(error){
        console.error(error)
        onSaved(null); return null
    }
}

function UploadDelivery({file,setFile,onSaved}:UploadDeliveryProps & {onSaved:(upload:{filename:string;session:string}|null)=>void}){
    const [session,setSession] = useState("")
    return (
    <section id="upload">
        <div className="upload">
            <h2>Upload a delivery</h2>
            <label htmlFor="file">Upload a file: </label>
            <input type="file" id="file"
            onChange={(event)=>{
                const selected = event.target.files?.[0] ?? null
                setFile(selected)
                console.log("Uploaded file: " + selected?.name)
                onSaved(null)
            }}/>
            <p>{file?.name ?? "No file selected"}</p>
            <label htmlFor="session">Session date/folder: </label>
            <input type="text" id="session" value={session} placeholder="e.g. 2026-11-20"
            onChange={(event)=>{setSession(event.target.value); onSaved(null)}}/>
            <button type="button" disabled={!file || !session.trim()}
            onClick={()=>
                SaveDelivery({file,session:session.trim(),onSaved})}>Save upload</button>
        </div>
      </section>
    )
}

export default UploadDelivery
