[TODO Check Mouad]

1. Sample run results with different models on the subset of "14" SRs (eval=True) are shown with source fields
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






2. Test performance / GPT classifier (on data/test.csv)
<table>
<tr>      precision    recall  f1-score   support </tr>

<tr>       False       1.00      0.99      1.00       234</tr>
<tr>        True       0.91      1.00      0.95        20</tr>

<tr>    accuracy                           0.99       254</tr>
   
<tr>   macro avg       0.95      1.00      0.97       254</tr>
   
<tr>weighted avg       0.99      0.99      0.99       254</tr>

</table>



