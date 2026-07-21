import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";
import type { Requirements,JobsDataType } from "../../types/api";

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
     
    const [editStatusId,setEditStatusId] = useState<string>("");

    const [editStatusName,setEditStatusName] = useState<string>("");

    const [editStatusValue,setEditStatusValue] = useState<string>("");

    const [editJobIsActive,setEditJobIsActive] = useState<boolean>(true);

    const[selectJobId,setSelectJobId] = useState<string>("");

    const[editRequiredStatusId,setEditRequiredStatusId] = useState<string>("");

    const [editRequiredStatusValue,setEditRequiredStatusValue] = useState<string>("");

    const [editRequirementIsActive,setEditRequirementIsActive] = useState<boolean>(true);

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

            setAddStatusName("");
            setAddStatusType("front");
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
                "status_name":addStatusName,
                "status_type":addStatusType,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editStatusSubmit(){
        if(editingId === "") return;
        
        try{
            await handleEdit(editingId,editStatusName,editStatusType,editStatusIsActive);
            await fetchStatusesData();

            setEditingId("");
            setEditStatusName("");
            setEditStatusType("front");
            setEditStatusIsActive(true);
        }catch(error){
            console.error(error);
        }
    }

    async function handleEdit(
        editingId:string,
        editStatusName:string,
        editStatusType:string,
        editStatusIsActive:boolean
        )
        {
        const response = await fetch("/api/admin/statuses/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "status_id":editingId,
                "status_name":editStatusName,
                "status_type":editStatusType,
                "status_is_active":editStatusIsActive,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    function startEditing(status:StatusesType){
        setEditingId(status.id);
        setEditStatusName(status.name);
        setEditStatusType(status.type);
        setEditStatusIsActive(status.isActive);
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
            <form onSubmit={addhandleSubmit}>
                <input 
                    type="text" 
                    value={addJobName} 
                    placeholder="職業名" 
                    required
                />
                {addRequirements.map((requirement,index) => (
                    <div key={index}>
                        <select
                            value={requirement.statusId}
                            onChange={(e) => {
                                const statusId =
                                    e.target.value === "" ? "" : Number(e.target.value);

                                addRequirement()
                                
                            }}>
                    
                            </select>
                    </div>
                ))}
                
                        
                <input type="number" name="required_status1_value" placeholder="ステータス値1" required>
                <select name="status_id_2">
                    {% for status in master_statuses %}
                    <option value="{{status[0]}}">
                        {{status[0]}}:{{status[1]}}:{{status[2]}}
                    </option>
                    {% endfor %}
                <input type="number" name="required_status2_value" placeholder="ステータス値2" required>
                <button type="submit">追加</button> 
            </form>

            <table border="1">
                <tr>
                    <th>ID</th>
                    <th>職業名</th>
                    <th>ステータス名１</th>
                    <th>必要ステータス値１</th>
                    <th>ステータス名２</th>
                    <th>必要ステータス値２</th>
                </tr>

                {% for id,job_name,status_name_1,requirement_status1_value,status_name_2,
                        requirement_status2_value,is_active,is_default in master_jobs %}
                <tr>
                    <td>{{id}}</td>
                    <td>{{job_name}}</td>
                    <td>{{status_name_1}}</td>
                    <td>{{requirement_status1_value}}</td>
                    <td>{{status_name_2}}</td>
                    <td>{{requirement_status2_value}}</td>
                    <td>{{is_default}}</td>
                    <td>
                    <form method="POST" action="{{url_for('admin_toggle_jobs')}}">
                        <input type="hidden" name="job_id" value="{{id}}">
                        {% if is_active %}
                        <button type="submit">無効化</button>
                        {% else %}
                        <button type="submit">有効化</button>
                        {% endif %}
                    </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    )
    
}
export default AdminJobs