interface analyseProps{
    file:File|null
}
function AnalyseVideo({file}:analyseProps){
    return (
    <button
        type="button"
        onClick = {()=>{
            if (file !== null){
                console.log(file.name)
            }else{
                console.log("File could not be read")
            }
        }}>
        
    Analyse Video</button>
    )
}
export default AnalyseVideo