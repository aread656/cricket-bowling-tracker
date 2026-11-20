interface analyseProps{
    file:File|null
}

async function GetVideo({file}:analyseProps){
    const url = "http://localhost:8080/api/analyse";
    try{
        const response = await fetch(url,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({filename:file?.name})
        });
        if (!response.ok){
            const msg = await response.text()
            throw new Error(`Response status: ${response.status}: ${msg}`);
        }
        const result = await response.json();
        return result
    }catch (error){
        console.error(error);
        return null
    }
}

function AnalyseVideo({file}:analyseProps){
    return (
    <button
        className="analyse-button"
        disabled={file === null}
        type="button"
        onClick = {()=>{
            if (file !== null){
                console.log(file.name)
                GetVideo({file}).then(result=>{
                    console.log(result)
                })
            }else{
                console.log("File could not be read")
            }
        }}>
        
    <span aria-hidden="true">↗</span> Analyse video</button>
    )
}
export default AnalyseVideo
