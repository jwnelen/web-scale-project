import React, {useEffect} from 'react';
import {get} from './apiClient'

function App() {
  useEffect(() => {
    const res = get('/products')
    console.log(res)

  })

  return (
    <div style={{textAlign: 'center'}}>
      <header>
        <h1>Welcome to the online store!</h1>
        <div style={{maxWidth: "10rem"}}>
          <ul>
            <li>Home</li>
            <li>Products</li>
            <li>Cart</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
