import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";
import type { StatusRulesDataType,StatusRulesType } from "../../types/api";
import styles from "../../styles/admin/AdminRules.module.css";


function AdminRules(){
    const [StatusRulesData,setStatusRulesData] =useState<StatusRulesDataType | null>(null);
    
    const navigate = useNavigate()

    const [addCategoryId,setAddCategoryId] = useState<string>("");

    const [addStatusId,setAddStatusId] = useState<string>("")

    const [addGainHours,setAddGainHours] =useState<number | null>(null);

    const [editCategoryId,setEditCategoryId]=useState<string>("");

    const [editStatusId,setEditStatusId]=useState<string>("");

    const [editGainHours,setEditGainHours] = useState<number | null>(null);

    const [editStatusRulesIsActive,setEditStatusRulesIsActive] = useState<boolean>(true);

    const [editingId,setEditingId] = useState<string>("");

    const [deleteId,setDeleteId] = useState<string>("");

    const [csvFile,setCsvFile] = useState<File | null>(null);

    useEffect(() => {
                fetchStatusRulesData();
            },[navigate]);

    if (!StatusRulesData){
        return <div>Loading...</div>;
    }

    const statusRules = StatusRulesData.statusRules

    const masterCategories = StatusRulesData.masterCategories

    const masterStatuses = StatusRulesData.masterStatuses

    async function fetchStatusRulesData(){
        try{
            const response = await fetch("/api/admin/status_rules");
            if(response.status === 401){
                navigate("/login");
                return;
            }
            if(!response.ok){
                throw new Error("データの取得に失敗しました");
            }
            const data: StatusRulesDataType = await response.json();
            setStatusRulesData(data);
        } catch (error){
            console.error(error);
        }
    }
        
     async function addHandleSubmit(e: React.FormEvent<HTMLElement>){
        e.preventDefault();

        if(
            addCategoryId === "" ||
            addStatusId === "" ||
            addGainHours === null
        )return;

        try{
            await handleAdd();
            await fetchStatusRulesData();

            setAddCategoryId("");
            setAddStatusId("");
            setAddGainHours(null);
        }catch(error){
            console.error(error);
        }
    }

    async function handleAdd(){
        const response = await fetch("/api/admin/status_rules/add", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "category_id":addCategoryId,
                "status_id":addStatusId,
                "gain_per_hours":addGainHours,
            }),
        });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function editStatusRulesSubmit(){
        if(editingId === "" ||
            editCategoryId === "" ||
            editStatusId === "" ||
            editGainHours === null
        )return;
       
        try{
            await handleEdit(editingId,editCategoryId,editStatusId,editGainHours,editStatusRulesIsActive);
            await fetchStatusRulesData();

            setEditingId("");
            setEditCategoryId("");
            setEditStatusId("");
            setEditGainHours(null);
            setEditStatusRulesIsActive(true);
        }catch(error){
            console.error(error);
        }
    }

    async function handleEdit(
        editingId:string,
        editCategoryId:string,
        editStatusId:string,
        editGainHours:number,
        editStatusRulesIsActive:boolean,
        )
        {
        const response = await fetch("/api/admin/status_rules/edit", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "id":editingId,
                "category_id":editCategoryId,
                "status_id":editStatusId,
                "gain_per_hours":editGainHours,
                "status_rules_is_active":editStatusRulesIsActive,
        }),
    });
        if(!response.ok){
            throw new Error("保存に失敗しました");
        }
        const result = await response.json();
        return result;
    }

    async function deleteStatusRulesSubmit(statusRuleId:string){
        if(statusRuleId === "")return;

        try{
            setDeleteId(statusRuleId);
            await handleDelete(statusRuleId);
            await fetchStatusRulesData();

            if(editingId === statusRuleId){
                setEditingId("");
                setEditCategoryId("");
                setEditStatusId("");
                setEditGainHours(null);
                setEditStatusRulesIsActive(true);
            }
        }catch(error){
            console.error(error);
        }finally{
            setDeleteId("");
        }
    }

    async function handleDelete(statusRuleId:string){
        const response = await fetch("/api/admin/status_rules/delete", {
            method:"POST",
            headers:{
                "Content-Type":"application/json",
            },
            body:JSON.stringify({
                "id":statusRuleId,
            }),
        });
        if(!response.ok){
            throw new Error("削除に失敗しました");
        }
        const result = await response.json();
        return result;
    }
    
     function startEditing(statusRule:StatusRulesType){
        if(editingId === statusRule.id){
            setEditingId("");
            return;
        }
            setEditingId(statusRule.id);
            setEditCategoryId(statusRule.category_id);
            setEditStatusId(statusRule.status_id);
            setEditGainHours(statusRule.gain_per_hours);
            setEditStatusRulesIsActive(statusRule.is_active);
        }

    async function importCsvSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        if (!csvFile) return;

        try{
            const formData = new FormData();
            formData.append("file", csvFile);

            const response = await fetch("/api/admin/status_rules/import", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message);
            }
            await fetchStatusRulesData();
            setCsvFile(null);
        }catch(error){
            console.error(error);
        }
    }
        
    
    return(
        <div className={styles.page}>
            <h2 className={styles.title}>ステータス上昇ルール管理</h2>
            <h3>追加</h3>
            <form className={styles.form} onSubmit={addHandleSubmit}>
                <select 
                    value={addCategoryId}
                    onChange={(e) => setAddCategoryId(e.target.value)}>
                    <option>カテゴリー選択</option>
                    {masterCategories.map((category) => {
                        return(
                            <option 
                                key={category.id}
                                value={category.id}
                            >
                                {category.id} : {category.name}
                            </option>
                        )
                    })}
                </select>
                <select 
                    value={addStatusId}
                    onChange={(e) => setAddStatusId(e.target.value)}>
                    <option>ステータス選択</option>
                    {masterStatuses.map((status) => {
                        return(
                            <option 
                                key={status.id}
                                value={status.id}
                            >
                                {status.id} : {status.name}
                            </option>
                        )
                    })}
                </select> 
                <input 
                    type="number" 
                    value={addGainHours ?? ""} 
                    onChange={(e) => setAddGainHours(e.target.value ==="" ? null:Number(e.target.value))}
                    placeholder="上昇量/h" 
                    required/>
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
                        <th>カテゴリー名</th>
                        <th>ステータス名</th>
                        <th>上昇量/h</th>
                        <th>有効化・無効化</th>
                        <th>編集・変更</th>
                        <th>削除</th>
                    </tr>
                </thead>
                <tbody>
                    {statusRules.map((statusRule) => {
                    return(
                            <tr
                                key={statusRule.id}
                                className={editingId === statusRule.id ? styles.editingRow : ""}
                            >
                                <td>{statusRule.id}</td>
                                <td>
                                    <span>{statusRule.category_name}</span>
                                    <select
                                        value={editCategoryId}
                                        disabled={editingId !== statusRule.id}
                                        onChange={(e) => setEditCategoryId(e.target.value)}
                                    >
                                        <option>カテゴリー選択</option>
                                        {masterCategories.map((category) => {
                                            return(
                                                <option 
                                                    key={category.id}
                                                    value={category.id}
                                                >
                                                    {category.id}:{category.name}
                                                </option>
                                            )
                                        })}
                                    </select>
                                </td>
                                <td>
                                    <span>{statusRule.status_name}</span>
                                    <select
                                        value={editStatusId}
                                        disabled={editingId !== statusRule.id}
                                        onChange={(e) => setEditStatusId(e.target.value)}
                                    >   
                                        <option>ステータス選択</option>
                                        {masterStatuses.map((status) => {
                                            return(
                                                <option 
                                                    key={status.id}
                                                    value={status.id}
                                                >
                                                    {status.id}:{status.name}
                                                </option>
                                            )
                                        })}  
                                    </select>
                                </td>
                                <td>
                                    <span>{statusRule.gain_per_hours}</span>
                                    <input
                                        type="text"
                                        value={editGainHours ?? ""}
                                        disabled={editingId !== statusRule.id}
                                        onChange={(e) => setEditGainHours(e.target.value === "" ? null: Number(e.target.value))}
                                    >
                                    </input>
                                </td>
                                <td>
                                    <select
                                        value={editingId === statusRule.id 
                                            ? String(editStatusRulesIsActive) 
                                            : String(statusRule.is_active)
                                        }
                                        disabled={editingId !== statusRule.id}
                                        onChange={(e) => 
                                            setEditStatusRulesIsActive(
                                                e.target.value === "true")}
                                    >
                                        <option value="true">有効</option>
                                        <option value="false">無効</option> 
                                    </select>
                                </td>   
                                <td>
                                <button
                                    type="button"
                                    onClick={() =>{                                  
                                        startEditing(statusRule)
                                    } }>
                                    {editingId === statusRule.id ? "キャンセル" : "編集"}
                                </button>
                                <button 
                                    type="button"
                                    disabled={editingId !== statusRule.id}
                                    onClick={() =>{
                                        editStatusRulesSubmit()
                                    }}>
                                    変更
                                </button>
                                </td>
                                <td>
                                    <button
                                        type="button"
                                        disabled={deleteId === statusRule.id}
                                        onClick={() =>{
                                            deleteStatusRulesSubmit(statusRule.id)
                                        }}>
                                        削除
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
export default AdminRules
