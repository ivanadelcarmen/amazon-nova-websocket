import { useState } from "react";
import "@aws-amplify/ui-react/styles.css";
import S2sChatBot from './s2s'


const App = ({ signOut, user }) => {
  const [displayTopMenu] = useState(window.self === window.top);

  return (
    <div>
      <S2sChatBot />
    </div>
  );
}
export default App;
