import { useEffect,useState,Fragment} from "react"
import { useNavigate } from "react-router-dom";
import type { Requirements,editRequirements,JobsType,JobsDataType, JobRequirementsType } from "../../types/api";

function AdminJobs(){
    const[jobsData,setJobsData] = useState<JobsDataType | null>(null);
    
    const navigate= useNavigate()

    const [addJobName,setAddJobName] = useState<string>("");

    const [addRequirements,setAddRequirements] = useState<Requirements[]>([
        {
            statusId:"",
            requiredValue:"",
        }
    ])

    const [editJobName,setEditJobName] = useState<string>("");

    const [editJobIsActive,setEditJobIsActive] = useState<boolean>(true);

    const [editJobIsDefault,setEditJobIsDefault] = useState<boolean>(true);

    const[selectJobId,setSelectJobId] = useState<string>("");

    const [editRequirements,setEditRequirements] = useState<editRequirements[]>([
        {
            id:"",
            statusId:"",
            requiredValue:"",
            isActive:true,
        }
    ])

    const [editingId,setEditingId] = useState<string>("");

    const [csvFile, setCsvFile] = useState<File | null>(null);

    useEffect(() => {
                fetchJobsData();
            },[navigate]);

     if (!jobsData){
        return <div>Loading...</div>;
    }

    const masterJobs = jobsData.masterJobs

    const jobRequirements = jobsData.jobRequirements

    const masterStatuses= jobsData.masterStatuses
    
    async function fetchJobsData(){
                    try{
                        const response = await fetch("/api/admin/jobs");
                        if(response.status === 401){
                            navigate("/login");
                            return;
                        }
                        if(!response.ok){
                            throw new Error("データの取得に失敗しました");
                        }
                        const data: JobsDataType = await response.json();
                        setJobsData(data);
                    } catch (error){
                        console.error(error);
                    }
                }

    

    async function addHandleSubmit(e: React.FormEvent<HTMLElement>){
        e.preventDefault();
        try{
            await handleAdd();
            await fetchJobsData();

            setAddJobName("");
            setAddRequirements([
            {
                statusId:"",
                requiredValue:"",
            }
            ]);
        }catch(error){
            console.error(error);
        }
    }

    async function handleAdd(){
        const response = await fetch("/api/admin/jobs/add", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "job_name":addJobName,
                "requirements":addRequirements,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editJobSubmit(){
        if(editingId === "") return;
        
        try{
            await handleEdit(editingId,editJobName,editJobIsActive,editJobIsDefault,editRequirements);
            await fetchJobsData();

            setEditingId("");
            setEditJobName("");
            setEditJobIsActive(true);
            setEditJobIsDefault(false);
            setEditRequirements(
                [
                {
                    id:"",
                    statusId:"",
                    requiredValue:"",
                    isActive:true,
                }
                ]
            );
        }catch(error){
            console.error(error);
        }
    }

    async function handleEdit(
        editingId:string,
        editJobName:string,
        editJobIsActive:boolean,
        editJobIsDefault:boolean,
        editRequirements:editRequirements[],
        )
        {
        const response = await fetch("/api/admin/jobs/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "job_id":editingId,
                "job_name":editJobName,
                "is_active":editJobIsActive,
                "is_default":editJobIsDefault,
                "requirements":editRequirements,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    function startEditing(job:JobsType,jobRequirements:JobRequirementsType[]){
        setEditingId(job.id);
        setEditJobName(job.job_name);
        setEditJobIsActive(job.is_active);
        setEditJobIsDefault(job.is_default);

        const targetRequirements = jobRequirements
            .filter((req) => req.job_id=job.id)
            .map((req) => ({
                id:req.id,
                statusId:req.required_status_id,
                requiredValue:req.required_status_value,
                isActive:req.is_active,
            }))
        setEditRequirements(targetRequirements);
    }

    
    async function importCsvSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        if (!csvFile) return;

        try{
            const formData = new FormData();
            formData.append("file", csvFile);

            const response = await fetch("/api/admin/jobs/import", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message);
            }
            await fetchJobsData();
            setCsvFile(null);
        }catch(error){
            console.error(error);
        }
    }

    const addRequirement = () =>{
        setAddRequirements((prev) => [
            ...prev,{
                statusId:"",
                requiredValue:"",
            },
        ]);
    };



    return(
        <div>
            <h2>職業管理</h2>
            <form onSubmit={addHandleSubmit}>
                <input 
                    type="text" 
                    value={addJobName} 
                    placeholder="職業名" 
                    onChange={(e) =>{setAddJobName(e.target.value)}}
                    required
                />
                {addRequirements.map((requirement,index) => (
                    <div key={index}>
                        <select
                            value={requirement.statusId}
                            onChange={(e) => {
                                const statusId = e.target.value 
                                setAddRequirements((prev) =>
                                    prev.map((item,itemIndex) =>
                                        itemIndex === index
                                        ? {...item,statusId}
                                        : item
                                    )
                                )
                            }}
                            required
                        >
                            <option value="">ステータスを選択</option>
                            {masterStatuses.map((status) => (
                                <option key={status.id} value={status.id}>
                                    {status.name}
                                </option>
                            ))}
                        </select>
                        <input
                            type="text"
                            value={requirement.requiredValue}
                            placeholder="必要値"
                            onChange={(e) => {
                                const requiredValue = e.target.value 

                                setAddRequirements((prev) =>
                                    prev.map((item,itemIndex) =>
                                        itemIndex === index
                                        ? {...item,requiredValue}
                                    :item
                                )
                            )
                            }}
                            required
                        />
                    </div>
                ))}
                <button type="button" onClick={addRequirement}>
                    必要ステータスを追加
                </button>
                <button type="submit">追加</button>
            </form>

            <form onSubmit={importCsvSubmit}>
                <input
                    type="file"
                    accept=".csv,text/csv"
                    onChange={(e) => {
                        setCsvFile(e.target.files?.[0] ?? null);
                    }}
                />
                <button type="submit" disabled={!csvFile}>
                    CSV一括追加
                </button>
            </form>

            <table>
                <tr>
                    <th>ID</th>
                    <th>職業名</th>
                    <th>必要ステータス</th>
                    <th>有効・無効</th>
                    <th>デフォルト</th>
                </tr>

                {masterJobs.map((job) => {
                    return(
                        <Fragment key={job.id}>
                        <tr
                            key={job.id}
                            className={editingId === job.id ? "editing-row" :""}
                            onClick={() => setSelectJobId(job.id)}
                        >
                            <td>{job.id}</td>
                            <td>
                                <div>{job.job_name}</div>
                                <input
                                    type="text"
                                    value={editJobName}
                                    disabled={editingId !== job.id}
                                    onChange={(e) => setEditJobName(e.target.value)}
                                    placeholder="職業名"
                                />
                            </td>
                            <td>
                                {jobRequirements
                                    .filter((req) => req.job_id === job.id)
                                    .map((req) => req.required_status_name)
                                    .join("・")   
                            }
                            </td>
                            <td>
                                <select
                                value={editingId === job.id 
                                    ? String(editJobIsActive) 
                                    : String(job.is_active)
                                }
                                disabled={editingId !== job.id}
                                onChange={(e) => 
                                    setEditJobIsActive(
                                        e.target.value === "true")}
                                >
                                    <option value="true">有効</option>
                                    <option value="false">無効</option> 
                                </select>
                            </td>
                            <td>
                                <select
                                value={editingId === job.id 
                                    ? String(editJobIsDefault) 
                                    : String(job.is_default)
                                }
                                disabled={editingId !== job.id}
                                onChange={(e) => 
                                    setEditJobIsDefault(
                                        e.target.value === "true")}
                                >
                                    <option value="true">有効</option>
                                    <option value="false">無効</option> 
                                </select>
                            </td>
                            <td><button
                                    type="button"
                                    onClick={() =>{                                  
                                        startEditing(job,jobRequirements)
                                    } }>
                                    編集
                                </button>
                                <button 
                                    type="button"
                                    disabled={editingId !== job.id}
                                    onClick={() =>{
                                        editJobSubmit()
                                    }}>
                                    変更
                                </button>
                            </td> 
                        </tr>
                        {(selectJobId === job.id || editingId === job.id)
                             && (
                            jobRequirements
                                .filter((req) => req.job_id === job.id)
                                .map((req,index) => (
                                    <tr key={req.id} >
                                        <td>{req.id}</td>
                                        <td>
                                            {editingId === job.id ? (
                                            <select
                                            value={editRequirements[index]?.statusId ?? ""}
                                            onChange={(e) => {
                                                const statusId = e.target.value 

                                                setEditRequirements((prev) =>
                                                prev.map((item, itemIndex) =>
                                                    itemIndex === index
                                                    ? { ...item, statusId }
                                                    : item
                                                )
                                                );
                                            }}
                                            >
                                                <option value="">ステータスを選択</option>

                                                {masterStatuses.map((status) => (
                                                    <option key={status.id} value={status.id}>
                                                    {status.name}
                                                    </option>
                                                ))}
                                            </select>
                                        ) : (
                                            req.required_status_name
                                        )}                        
                                        </td>
                                        <td>
                                            <input
                                            type="text"
                                            value={editingId === job.id
                                                ? editRequirements[index]?.requiredValue ?? ""
                                                : req.required_status_value
                                            }
                                            disabled={editingId !== job.id}
                                            onChange={(e) => {
                                                const requiredValue = e.target.value 

                                                setEditRequirements((prev) =>
                                                    prev.map((item,itemIndex) =>
                                                        itemIndex === index
                                                        ? {...item,requiredValue}
                                                    :item
                                                    )
                                                )
                                            }}
                                        />
                                        </td>
                                        <td>
                                            <select
                                                value={editingId === job.id 
                                                    ? String(editRequirements[index]?.isActive ?? true)
                                                    : String(req.is_active)
                                                }
                                                disabled={editingId !== job.id}
                                                onChange={(e) => {
                                                    const isActive = e.target.value === "true";

                                                    setEditRequirements((prev) =>
                                                    prev.map((item,itemIndex) =>
                                                        itemIndex === index
                                                        ? {...item,isActive}
                                                    :item
                                                    )
                                                    )
                                                }}
                                            >
                                                    <option value="true">有効</option>
                                                    <option value="false">無効</option> 
                                            </select>
                                        </td>
                                        
                                    </tr>
                                ))
                                
                                
                            
                        
                        )}
                        </Fragment>
                    )
                })}
                
            </table>
        </div>
    )
    
}
export default AdminJobs