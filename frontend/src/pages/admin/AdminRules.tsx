import { useEffect,useState} from "react"
import { useNavigate } from "react-router-dom";


function AdminRules{
    const [StatusRulesData,setStatusRulesData] =useState<AchievementsDataType | null>(null);
    
    const navigate = useNavigate()

    const [addCategoryId,setAddCategoryId] = useState<string>("");

    const [addStatusId,setAddStatusId] = useState<string>("")

    const [addGainHours,setAddGainHours] =useState<string>("");

    const [editCategoryId,setEditCategoryId]=useState<string>("");

    const [editHours,setEditHours] = useState<number | null>(null)

    const [editAchievementName,setEditAchievementName] = useState<string>("");

    const [editTitleName,setEditTitleName] =useState<string>("");

    const [editAchievementIsActive,setEditAchievementIsActive] = useState<boolean>(true);

    const [editingId,setEditingId] = useState<string>("");

    const [csvFile,setCsvFile] = useState<File | null>(null);


    
    return(
        <div>
            <h2>ステータス上昇ルール管理</h2>
            <form onSubmit={addHandleSubmit}>
                <select 
                    value={addCategoryId}
                    onChange={(e) => setAddCategoryId(e.target.value)}>

                    {masterCategories.map((category) => {
                        return(
                            <option value={category.id}>
                                {category.id} : {category.name}
                            </option>
                        )
                    })}
                </select>
                <select 
                    value={addStatusId}
                    onChange={(e) => setAddStatusId(e.target.value)}>

                    {masterStatuses.map((status) => {
                        return(
                            <option value={status.id}>
                                {status.id} : {status.name}
                            </option>
                        )
                    })}
                </select> 
                <input 
                    type="number" 
                    value={addGainHours} 
                    onChange={(e) => setAddGainHours(e.target.value)}
                    placeholder="上昇量/h" 
                    required/>
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
                    <th>カテゴリー名</th>
                    <th>ステータス名</th>
                    <th>上昇量/h</th>
                    <th>有効化・無効化</th>
                </tr>

                {statusRules.map(rule) => {
                    return(
                        <tr>
                            <td>{rule.id}</td>
                            <td>{{category_id}}</td>
                            <td>{{category_name}}</td>
                            <td>{{status_id}}</td>
                            <td>{{status_name}}</td>
                            <td>{{gain_per_hours}}</td>
                            <td>
                            <form method="POST" action="{{url_for('admin_delete_status_rules')}}">
                                <input type="hidden" name="category_id" value="{{category_id}}">
                                <input type="hidden" name="status_id" value="{{status_id}}">
                                <button type="submit">削除</button>
                            </form>
                        </tr>
                    )
                }}
            </table>
        </div>

    )
    
}
export default AdminRules