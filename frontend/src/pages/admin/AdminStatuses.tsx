import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";

import type { StatusesType,StatusesDataType } from "../../types/api";
import styles from "../../styles/admin/AdminStatuses.module.css";

function AdminStatuses(){
    const[StatusesData,setStatusesData] = useState<StatusesDataType | null>(null);

    const navigate= useNavigate()

    const [addStatusName,setAddStatusName] = useState<string>("");

    const [addStatusDefaultValue,setAddStatusDefaultValue] = useState<string>("");

    const [addStatusType,setAddStatusType] = useState<"front" | "back">("front");

    const [editStatusName,setEditStatusName] = useState<string>("");

    const [editStatusType,setEditStatusType] = useState<"front" | "back">("front");

    const [editStatusDefaultValue,setEditStatusDefaultValue] = useState<string>("");

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

        if(
            addStatusName === "" ||
            addStatusDefaultValue === "" 
        ) return;

        try{
            await handleAdd();
            await fetchStatusesData();

            setAddStatusName("");
            setAddStatusDefaultValue("");
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
                "default_value":addStatusDefaultValue,
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
        if(
            editingId === "" ||
            editStatusName === "" ||
            editStatusDefaultValue === ""
        ) return;
       
        try{
            await handleEdit(
                editingId,
                editStatusName,
                editStatusDefaultValue,
                editStatusType,
                editStatusIsActive
            );
            await fetchStatusesData();

            setEditingId("");
            setEditStatusName("");
            setEditStatusType("front");
            setEditStatusDefaultValue("");
            setEditStatusIsActive(true);
        }catch(error){
            console.error(error);
        }
    }

    async function handleEdit(
        editingId:string,
        editStatusName:string,
        editStatusDefaultValue:string,
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
                "default_value":editStatusDefaultValue,
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
        setEditStatusDefaultValue(status.default_value);
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
        <div className={styles.page}>
            <h2 className={styles.title}>ステータス追加</h2>
            <h3>追加</h3>
            <form className={styles.form} onSubmit={addHandleSubmit}>
                <input 
                    type="text" 
                    value={addStatusName} 
                    onChange={(e) => setAddStatusName(e.target.value)}
                    placeholder="ステータス名" 
                    required
                />
                <input 
                    type="text" 
                    value={addStatusDefaultValue} 
                    onChange={(e) => setAddStatusDefaultValue(e.target.value)}
                    placeholder="デフォルト値" 
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
                        <th>ステータス名</th>
                        <th>デフォルト値</th>
                        <th>ステータスタイプ</th>
                        <th>有効・無効</th>
                        <th>編集・変更</th>
                    </tr>
                </thead>
                <tbody>
                    {masterStatuses.map((status) => {

                    return(
                        <tr 
                            key={status.id} 
                            className={editingId === status.id ? styles.editingRow : ""}
                        >
                        <td>{status.id}</td>
                        <td>
                            <div className={styles.field}>
                            <span>{status.name}</span>
                            <input 
                            type="text" 
                            value={editingId === status.id ? editStatusName : status.name}
                            disabled={editingId !== status.id}
                            onChange={(e) => setEditStatusName(e.target.value)}
                            placeholder="ステータス名"
                            />
                            </div>
                        </td>
                        <td>
                            <div className={styles.field}>
                            <span>{status.default_value}</span>
                            <input 
                            type="text" 
                            value={editingId === status.id ? editStatusDefaultValue : status.default_value}
                            disabled={editingId !== status.id}
                            onChange={(e) => setEditStatusDefaultValue(e.target.value)}
                            placeholder="デフォルト値"
                            />
                            </div>
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
                </tbody>
            </table>
        </div>
    )
}
export default AdminStatuses;
