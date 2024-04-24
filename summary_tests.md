
1. Sample run results with different models on a subset of SRs (eval=True) are shown with source fields
 (Problem Description: PD, Customer Symptoms: CS, and Resolution Summary: RS)

<table>
<tr> Accuracy for Software Version Prediction </tr>
<tr>
<td>setting/model</td>
<td>gpt-3.5-turbo-0125</td>
<td>gpt-4-0125-preview</td>
<td>gpt-3.5-turbo-instruct</td>
</tr>
<tr>
<td>CS+PD+RS</td>
<td>0.92</td>
<td>0.85</td>
<td>0.85</td>
</tr>
<tr>
<td>CS+PD</td>
<td>0.78</td>
<td>0.71</td>
<td>0.64</td>
</tr>
</table>


<table>
<tr> Accuracy for Product Names Prediction </tr>
<tr>
<td>setting/model</td>
<td>gpt-3.5-turbo-0125</td>
<td>gpt-4-0125-preview</td>
<td>gpt-3.5-turbo-instruct</td>
</tr>
<tr>
<td>CS+PD+RS</td>
<td>0.78</td>
<td>0.85</td>
<td>0.5</td>
</tr>
<tr>
<td>CS+PD</td>
<td>0.71</td>
<td>0.85</td>
<td>0.35</td>
</tr>
</table>






2. Test performance / GPT classifier software version (on data/test.csv)
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.99  </td>  <td>  0.98  </td>   <td> 0.99   </td>   <td> 1589</td></tr>
<tr><td>        True</td>    <td>   0.80  </td>   <td> 0.86  </td>  <td>  0.83  </td>   <td>   125</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.97  </td>   <td>  1714</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.90 </td>   <td>  0.92 </td>    <td> 0.91 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.98  </td>   <td> 0.97 </td>  <td>   0.97</td>     <td>  254</td></tr>

</table>

3. Test performance / GPT classifier product name (on data/test.csv)
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.89  </td>  <td>  0.89  </td>   <td> 0.89   </td>   <td> 1305</td></tr>
<tr><td>        True</td>    <td>   0.65  </td>   <td> 0.63  </td>  <td>  0.64  </td>   <td>   409</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.83  </td>   <td>  1714</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.77 </td>   <td>  0.76 </td>    <td> 0.76 </td>   <td>   1714</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.83  </td>   <td> 0.83 </td>  <td>   0.83</td>     <td>  1714</td></tr>

</table>

