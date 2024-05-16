
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






2. Test performance / send to GPT or not (SWV) classifier  (on filter_training/data/test.csv )
   * flanT5-large
    <table>
    <tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>
    
    <tr><td>       False</td>    <td>   1.00  </td>  <td>  0.99  </td>   <td> 1.00   </td>   <td> 234</td></tr>
    <tr><td>        True</td>    <td>   0.91  </td>   <td> 1.00  </td>  <td>  0.95  </td>   <td>   20</td></tr>
    
    <tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.99  </td>   <td>  254</td></tr>
       
    <tr><td>   macro avg</td>    <td>   0.95 </td>   <td>  1.00 </td>    <td> 0.97 </td>   <td>   254</td></tr>
       
    <tr><td>weighted avg </td>   <td>   0.99  </td>   <td> 0.99 </td>  <td>   0.99</td>     <td>  254</td></tr>
    
    </table>

2. Test performance / send to GPT or not (SWV) classifier flanT5-base (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   1.00  </td>  <td>  0.97  </td>   <td> 0.99   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.77  </td>   <td> 1.00  </td>  <td>  0.87  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.98  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.88 </td>   <td>  0.99 </td>    <td> 0.93 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.98  </td>   <td> 0.98 </td>  <td>   0.98</td>     <td>  254</td></tr>

</table>

2. Test performance / send to GPT or not (SWV) classifier T5-large (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.99  </td>  <td>  0.98  </td>   <td> 0.98   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.78  </td>   <td> 0.90  </td>  <td>  0.84  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.97  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.89 </td>   <td>  0.94 </td>    <td> 0.91 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.97  </td>   <td> 0.97 </td>  <td>   0.97</td>     <td>  254</td></tr>

</table>

2. Test performance / send to GPT or not (SWV) classifier T5-base (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.99  </td>  <td>  1.00  </td>   <td> 0.99   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.94  </td>   <td> 0.85  </td>  <td>  0.89  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.98  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.97 </td>   <td>  0.92 </td>    <td> 0.94 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.98  </td>   <td> 0.98 </td>  <td>   0.98</td>     <td>  254</td></tr>

</table>

2. Test performance / send to GPT or not (SWV) classifier roberta-large (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.99  </td>  <td>  0.96  </td>   <td> 0.97   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.63  </td>   <td> 0.85  </td>  <td>  0.72  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.95  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.81 </td>   <td>  0.90 </td>    <td> 0.85 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.96  </td>   <td> 0.95 </td>  <td>   0.95</td>     <td>  254</td></tr>

</table>

2. Test performance / send to GPT or not (SWV) classifier bert-base-uncased (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.99  </td>  <td>  0.96  </td>   <td> 0.97   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.64  </td>   <td> 0.90  </td>  <td>  0.75  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.95  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.82 </td>   <td>  0.93 </td>    <td> 0.86 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.96  </td>   <td> 0.95 </td>  <td>   0.96</td>     <td>  254</td></tr>

</table>

2. Test performance / send to GPT or not (SWV) classifier bert-large-uncased (on filter_training/data/test.csv )
<table>
<tr> <td></td> <td> precision</td>    <td>recall</td> <td> f1-score</td>   <td>support </td></tr>

<tr><td>       False</td>    <td>   0.92  </td>  <td>  1.00  </td>   <td> 0.96   </td>   <td> 234</td></tr>
<tr><td>        True</td>    <td>   0.00  </td>   <td> 0.00  </td>  <td>  0.00  </td>   <td>   20</td></tr>

<tr><td>    accuracy </td>     <td></td></td>    <td></td>             <td>         0.92  </td>   <td>  254</td></tr>
   
<tr><td>   macro avg</td>    <td>   0.46 </td>   <td>  0.50 </td>    <td> 0.48 </td>   <td>   254</td></tr>
   
<tr><td>weighted avg </td>   <td>   0.85  </td>   <td> 0.92 </td>  <td>   0.88</td>     <td>  254</td></tr>

</table>

