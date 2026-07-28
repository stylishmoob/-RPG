import { useEffect,useState,Fragment} from "react"
import { useNavigate } from "react-router-dom";
import type { JobRequirementInputType, JobsType, JobsDataType, JobRequirementType } from "../../types/api";
import styles from "../../styles/admin/AdminJobs.module.css";

function AdminJobs(){
    const[jobsData,setJobsData] = useState<JobsDataType | null>(null);
    
    const navigate= useNavigate()

    const [addJobName,setAddJobName] = useState<string>("");

    const [addRequirements,setAddRequirements] = useState<JobRequirementInputType[]>([
        {
            statusId:"",
            requiredValue:"",
        }
    ])

    const [editJobName,setEditJobName] = useState<string>("");

    const [editJobIsActive,setEditJobIsActive] = useState<boolean>(true);

    const [editJobIsDefault,setEditJobIsDefault] = useState<boolean>(true);

    const[selectJobId,setSelectJobId] = useState<string>("");

    const [editRequirements,setEditRequirements] = useState<JobRequirementType[]>([
        {
            id:"",
            jobId:"",
            statusId:"",
            statusName:"",
            requiredValue:"",
            isActive:true,
        }
    ])

    const [editingId,setEditingId] = useState<string>("");

    const [deleteJobId,setDeleteJobId] = useState<string>("");

    const [deleteRequirementKey,setDeleteRequirementKey] = useState<string>("");

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

        if(
            addJobName.trim() === "" ||
            addRequirements.length === 0 ||
            addRequirements.some((requirement) =>
                requirement.statusId === "" ||
                requirement.requiredValue === ""
            )  
        ) 
        {return};

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
                jobName:addJobName,
                requirements:addRequirements,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editJobSubmit(){
        if(
            editingId === ""   ||
            editJobName.trim() === "" ||
            editRequirements.length === 0 ||
            editRequirements.some((requirement) =>
                requirement.id === "" ||
                requirement.statusId === "" ||
                requirement.requiredValue === ""
            )  
        ) 
        {return};
        
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
                    jobId:"",
                    statusId:"",
                    statusName:"",
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
        editRequirements:JobRequirementType[],
        )
        {
        const response = await fetch("/api/admin/jobs/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                jobId:editingId,
                jobName:editJobName,
                isActive:editJobIsActive,
                isDefault:editJobIsDefault,
                requirements:editRequirements,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function deleteJobSubmit(jobId:string){
        if(jobId === "")return;

        try{
            setDeleteJobId(jobId);
            await handleDeleteJob(jobId);
            await fetchJobsData();

            if(editingId === jobId){
                setEditingId("");
                setEditJobName("");
                setEditJobIsActive(true);
                setEditJobIsDefault(false);
                setEditRequirements(
                    [
                    {
                        id:"",
                        jobId:"",
                        statusId:"",
                        statusName:"",
                        requiredValue:"",
                        isActive:true,
                    }
                    ]
                );
            }

            if(selectJobId === jobId){
                setSelectJobId("");
            }
        }catch(error){
            console.error(error);
        }finally{
            setDeleteJobId("");
        }
    }

    async function handleDeleteJob(jobId:string){
        const response = await fetch("/api/admin/jobs/delete", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                jobId,
            }),
        });
        if(!response.ok){
            throw new Error("削除に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function deleteJobRequirementSubmit(
        requirement:JobRequirementType,
        index:number,
        requirementKey:string,
    ){
        if(requirement.id === ""){
            setEditRequirements((prev) =>
                prev.filter((_,itemIndex) => itemIndex !== index)
            );
            return;
        }

        try{
            setDeleteRequirementKey(requirementKey);
            await handleDeleteJobRequirement(requirement.id);
            await fetchJobsData();

            if(editingId === requirement.jobId){
                setEditRequirements((prev) =>
                    prev.filter((item) => item.id !== requirement.id)
                );
            }
        }catch(error){
            console.error(error);
        }finally{
            setDeleteRequirementKey("");
        }
    }

    async function handleDeleteJobRequirement(requirementId:string){
        const response = await fetch("/api/admin/jobs/requirements/delete", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                requirementId,
            }),
        });
        if(!response.ok){
            throw new Error("削除に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    function startEditing(job:JobsType,jobRequirements:JobRequirementType[]){
        if(editingId === job.id){
            setEditingId("");
            return;
        }
        setEditingId(job.id);
        setEditJobName(job.jobName);
        setEditJobIsActive(job.isActive);
        setEditJobIsDefault(job.isDefault);

        const targetRequirements = jobRequirements
            .filter((req) => req.jobId === job.id)
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

    const pushRequirement = () =>{
        setEditRequirements((prev) => [
            ...prev,{
                id: "",
                jobId: editingId,
                statusId:"",
                statusName:"",
                requiredValue:"",
                isActive:true,
            },
        ])
    }

    const handleSelectJob = (jobId:string) => {
        setSelectJobId((prev) => (prev === jobId ? "" : jobId))
    }

    return(
        <div className={styles.page}>
            <h2 className={styles.title}>職業管理</h2>
            <h3>追加</h3>
            <form className={`${styles.form} ${styles.addForm}`} onSubmit={addHandleSubmit}>
                <div className={styles.addJobCell}>
                    <input
                        type="text"
                        value={addJobName}
                        placeholder="職業名"
                        onChange={(e) =>{setAddJobName(e.target.value)}}
                        required
                    />
                </div>
                <div className={styles.addRequirements}>
                    {addRequirements.map((requirement,index) => (
                        <div className={styles.requirementRow} key={index}>
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
                </div>
                <div className={styles.addActions}>
                    <button type="button" onClick={addRequirement}>
                        必要ステータスを追加
                    </button>
                    <button type="submit">追加</button>
                </div>
            </form>
            <h3>csv追加</h3>
            <form className={styles.form} onSubmit={importCsvSubmit}>
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
            <h3>編集</h3>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>職業名</th>
                        <th>必要ステータス</th>
                        <th>有効・無効</th>
                        <th>デフォルト</th>
                        <th>編集・変更</th>
                        <th>削除</th>
                    </tr>
                </thead>

                <tbody>
                    {masterJobs.map((job) => {
                    const isJobOpen = selectJobId === job.id || editingId === job.id;
                    const currentJobRequirements = jobRequirements.filter(
                            (req) => req.jobId === job.id
                    );
                    const visibleRequirements =
                        editingId === job.id ? editRequirements : currentJobRequirements;
                    return(
                        <Fragment key={job.id}>
                        <tr
                            className={`${styles.selectableRow} ${isJobOpen ? styles.openRow : ""} ${editingId === job.id ? styles.editingRow : ""}`}
                            onClick={() => handleSelectJob(job.id)}
                        >
                            <td>{job.id}</td>
                            <td>
                                <div className={styles.field}>
                                    <span>{job.jobName}</span>
                                    <input
                                        type="text"
                                        value={editingId === job.id ? editJobName : job.jobName}
                                        disabled={editingId !== job.id}
                                        onChange={(e) => setEditJobName(e.target.value)}
                                        placeholder="職業名"
                                    />
                                </div>
                            </td>
                            <td>
                                {visibleRequirements
                                    .map((req) => `${req.statusName}:${req.requiredValue}`)
                                    .join("・")
                            }
                            </td>
                            <td>
                                <select
                                value={editingId === job.id
                                    ? String(editJobIsActive)
                                    : String(job.isActive)
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
                                    : String(job.isDefault)
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
                                    onClick={(e) =>{
                                        e.stopPropagation();
                                        startEditing(job,jobRequirements)
                                    } }>
                                    {editingId === job.id ? "キャンセル" : "編集"}
                                </button>
                                <button 
                                    type="button"
                                    disabled={editingId !== job.id}
                                    onClick={(e) =>{
                                        e.stopPropagation();
                                        editJobSubmit()
                                    }}>
                                    変更
                                </button>
                            </td> 
                            <td>
                                <button
                                    type="button"
                                    disabled={deleteJobId === job.id}
                                    onClick={(e) =>{
                                        e.stopPropagation();
                                        deleteJobSubmit(job.id)
                                    }}>
                                    削除
                                </button>
                            </td>
                        </tr>
                        {isJobOpen
                             && (
                            <tr className={styles.requirementDetailRow}>
                                <td colSpan={7}>
                                    <div className={styles.requirementPanel}>
                                        <div className={styles.requirementHeader}>
                                            <h4>必要ステータス</h4>
                                            <button
                                                type="button"
                                                disabled={editingId !== job.id}
                                                onClick={pushRequirement}
                                                >
                                                ステータス追加
                                            </button>
                                        </div>
                                        {visibleRequirements.map((req,index) => {
                                            const requirementKey = req.id || `${job.id}-${index}`;

                                            return (
                                            <div className={styles.requirementItem} key={requirementKey}>
                                                <span className={styles.requirementId}>{req.id}</span>
                                                <div className={styles.requirementValues}>
                                                    <select
                                                        className={styles.requirementStatus}
                                                        value={req.statusId}
                                                        disabled={editingId !== job.id}
                                                        onChange={(e) => {
                                                            const statusId = e.target.value
                                                            const statusName =
                                                                masterStatuses.find((status) => status.id === statusId)?.name ?? ""

                                                            setEditRequirements((prev) =>
                                                            prev.map((item, itemIndex) =>
                                                                itemIndex === index
                                                                ? { ...item, statusId, statusName }
                                                                : item
                                                            )
                                                            );
                                                        }}
                                                    >
                                                        {masterStatuses.map((status) => (
                                                            <option key={status.id} value={status.id}>
                                                            {status.name}
                                                            </option>
                                                        ))}
                                                    </select>
                                                    <input
                                                        className={styles.requirementValue}
                                                        type="text"
                                                        value={req.requiredValue}
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
                                                </div>
                                                <select
                                                    className={styles.requirementActiveSelect}
                                                    value={String(req.isActive)}
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
                                                <button
                                                    className={styles.requirementDeleteButton}
                                                    type="button"
                                                    disabled={deleteRequirementKey === requirementKey}
                                                    onClick={() =>{
                                                        deleteJobRequirementSubmit(req,index,requirementKey)
                                                    }}>
                                                    削除
                                                </button>
                                            </div>
                                        )})}
                                    </div>
                                </td>
                            </tr>
                        )}
                        </Fragment>
                    )
                    })}
                </tbody>
            </table>
        </div>
    )
    
}
export default AdminJobs
