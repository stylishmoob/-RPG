import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";

import type { StatusesType,StatusesDataType } from "../../types/api";

function AdminStatuses(){
    const[StatusesData,setStatusesData] = useState<StatusesDataType | null>(null);

    const navigate= useNavigate()

    const [addStatusName,setAddStatusName] = useState<string>("");

    const [addStatusType,setAddStatusType] = useState<"front" | "back">("front");

    const [editStatusName,setEditStatusName] = useState<string>("");

    const [editStatusType,setEditStatusType] = useState<"front" | "back">("front");

    const [editStatusIsActive,setEditStatusIsActive] = useState<boolean>(true);

    const [editingId,setEditingId] = useState<string>("");

    const [csvFile, setCsvFile] = useState<File | null>(null);

    useEffect(() => {
                fetchStatusesData();
            },[navigate]);

    if (!StatusesData){
        return <div>Loading...</div>;
    }

    const masterStatuses = StatusesData.masterStatuses

    async function fetchStatusesData(){
                    try{
                        const response = await fetch("/api/admin/statuses");
                        if(response.status === 401){
                            navigate("/login");
                            return;
                        }
                        if(!response.ok){
                            throw new Error("データの取得に失敗しました");
                        }
                        const data: StatusesDataType = await response.json();
                        setStatusesData(data);
                    } catch (error){
                        console.error(error);
                    }
                }

    async function addHandleSubmit(e: React.FormEvent<HTMLElement>){
        e.preventDefault();

        try{
            await handleAdd();
            await fetchStatusesData();

            setAddStatusName("");
            setAddStatusType("front");
        }catch(error){
            console.error(error);
        }
    }

    async function handleAdd(){
        const response = await fetch("/api/admin/statuses/add", {
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

            const response = await fetch("/api/admin/statuses/import", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message);
            }
            await fetchStatusesData();
            setCsvFile(null);
        }catch(error){
            console.error(error);
        }
    }
        

    return(
        <div>
            <h2>ステータス追加</h2>
            <form onSubmit={addHandleSubmit}>
                <input 
                    type="text" 
                    value={addStatusName} 
                    onChange={(e) => setAddStatusName(e.target.value)}
                    placeholder="ステータス名" 
                    required
                />
                <select 
                    value={addStatusType}
                    onChange={(e) => setAddStatusType(e.target.value as "front" | "back")}>
                    <option value="front">front</option>
                    <option value="back">back</option>
                </select>
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
                    <th>ステータス名</th>
                    <th>ステータスタイプ</th>
                    <th>有効・無効</th>
                </tr>
                {masterStatuses.map((status) => {

                    return(
                        <tr 
                            key={status.id} 
                            className={editingId === status.id ? "editing-row" :""}
                        >
                        <td>{status.id}</td>
                        <td>
                            <div>{status.name}</div>    
                            <input 
                            type="text" 
                            value={editStatusName}
                            disabled={editingId !== status.id}
                            onChange={(e) => setEditStatusName(e.target.value)}
                            placeholder="ステータス名"
                            />
                        </td>
                        <td>
                            <select 
                                value={editingId === status.id ? editStatusType : status.type}
                                disabled={editingId !== status.id}
                                onChange={(e) => 
                                    setEditStatusType(
                                        e.target.value as "front" | "back"
                                    )
                                } 
                            >
                            <option value="front">front</option>
                            <option value="back">back</option>
                            </select>
                        </td>
                        <td>
                            <select
                                value={editingId === status.id 
                                    ? String(editStatusIsActive) 
                                    : String(status.isActive)
                                }
                                disabled={editingId !== status.id}
                                onChange={(e) => 
                                    setEditStatusIsActive(
                                        e.target.value === "true")}
                                >
                                <option value="true">有効</option>
                                <option value="false">無効</option> 
                            </select>
                        </td>
                        <td><button
                                type="button"
                                onClick={() =>{                                  
                                    startEditing(status)
                                } }>
                                編集
                            </button>
                            <button 
                                type="button"
                                disabled={editingId !== status.id}
                                onClick={() =>{
                                    editStatusSubmit()
                                }}>
                                変更
                            </button>
                        </td>
                        </tr>
                        )
                })}   
            </table>
        </div>
    )
    
}
export default AdminStatuses;